from collections import Counter

import networkx as nx
import numpy as np
import pandas as pd
import stellargraph as sg
from sklearn import feature_extraction
from sklearn import metrics as skmetrics
from sklearn.utils import class_weight
from stellargraph.layer import GraphSAGE
from stellargraph.mapper import GraphSAGENodeGenerator
from tensorflow.keras import layers, optimizers, losses, metrics, Model


def average_classifiers(classifiers):
    labels = ['sc_guard', 'cfi_verify', 'oh_verify', 'none']
    metric = 'fscore'
    tmp = {}
    for lbl in labels:
        tmp[lbl] = []
    for array in classifiers:
        for scores in array:
            if np.isnan(scores[metric]):
                continue
            tmp[scores['label']].append(scores[metric])
    output = {}
    for label in labels:
        output[label] = np.mean(tmp[label])
    return output


def build_gnx_network(relations_df):
    gnx = nx.Graph()
    relations_df = relations_df.loc[relations_df['label'].isin(['cfg'])]  # ['svgc','svgd','scc','cfg']
    gnx.add_edges_from(nx.from_pandas_edgelist(relations_df, edge_attr='label').edges(data=True))
    return gnx


class GraphSageSIPLocalizer:
    def __init__(self, num_epochs=7, k_folds=10, batch_size=50) -> None:
        super().__init__()
        self.num_epochs = num_epochs
        self.k_folds = k_folds
        self.batch_size = batch_size

    def train(self, data_dict, target_feature_name):
        results_data = {
            'data_source': data_dict['data_source'].name,
            'data_dir': data_dict['data_dir'].name,
            'results': self._run_train(data_dict, target_feature_name)
        }
        return results_data

    def _run_train(self, data_dict, target_feature_name):
        all_train_features = data_dict['train']['features'].get()
        train_blocks_df = data_dict['train']['blocks_df'].get()

        # because we split at the program level, relations don't need split
        relations_df = data_dict['train']['relations_df'].get()

        all_val_features = data_dict['val']['features'].get()
        val_blocks_df = data_dict['val']['blocks_df'].get()

        classifier_results = []
        train_data = pd.merge(train_blocks_df, all_train_features, on='uid')
        val_data = pd.merge(val_blocks_df, all_val_features, on='uid')
        all_features = pd.concat([all_train_features, all_val_features], axis=0)

        # remove unused graph edges
        relations_df = relations_df[
            relations_df.source.isin(all_features.index) & relations_df.target.isin(all_features.index)
        ]

        # remove unconnected nodes
        all_features = all_features.iloc[
            all_features.index.isin(relations_df.source) | all_features.index.isin(relations_df.target)
        ]
        gnx = build_gnx_network(relations_df)

        _, _, _, _, history, _, out_result = self._train_model(
            gnx, train_data, val_data, all_features, target_feature_name
        )
        classifier_results.append(out_result['classifier'])
        out_result['classifier'] = average_classifiers(classifier_results)

        return out_result

    def _train_model(self, gnx, train_data, test_data, all_features, target_feature_name):
        subject_groups_train = Counter(train_data[target_feature_name])
        subject_groups_test = Counter(test_data[target_feature_name])

        graph = sg.StellarGraph(gnx, node_features=all_features)

        output_results = {
            'train_size': len(train_data),
            'test_size': len(test_data),
            'subject_groups_train': subject_groups_train,
            'subject_groups_test': subject_groups_test,
            'graph_info': graph.info()
        }

        num_samples = [10, 5]
        generator = GraphSAGENodeGenerator(graph, self.batch_size, num_samples)

        target_encoding = feature_extraction.DictVectorizer(sparse=False)
        train_targets = target_encoding.fit_transform(train_data[[target_feature_name]].to_dict('records'))
        class_weights = class_weight.compute_class_weight(
            class_weight='balanced',
            classes=np.unique(train_data[target_feature_name].to_list()),
            y=train_data[target_feature_name].to_list()
        )
        class_weights = dict(enumerate(class_weights))
        test_targets = target_encoding.transform(test_data[[target_feature_name]].to_dict('records'))
        train_gen = generator.flow(train_data.index, train_targets, shuffle=True)
        graph_sage_model = GraphSAGE(
            layer_sizes=[80, 80],
            generator=generator,  # train_gen,
            bias=True,
            dropout=0.5,
        )
        print('building model...')

        x_inp, x_out = graph_sage_model.build()
        prediction = layers.Dense(units=train_targets.shape[1], activation="softmax")(x_out)

        model = Model(inputs=x_inp, outputs=prediction)
        print('compiling model...')
        model.compile(
            optimizer=optimizers.Adam(learning_rate=0.005),
            loss=losses.categorical_crossentropy,
            metrics=['acc', metrics.categorical_accuracy],
        )
        print('testing the model...')
        test_gen = generator.flow(test_data.index, test_targets)
        history = model.fit(
            train_gen,
            epochs=self.num_epochs,
            validation_data=test_gen,
            verbose=2,
            shuffle=True,
            class_weight=class_weights,
        )
        # save test metrics
        test_metrics = model.evaluate(test_gen)
        print('Test Set Metrics:')
        output_results['test_metrics'] = []
        for name, val in zip(model.metrics_names, test_metrics):
            output_results['test_metrics'].append({'name': name, 'val:': val})
            print("\t{}: {:0.4f}".format(name, val))

        test_nodes = test_data.index
        test_mapper = generator.flow(test_nodes)
        test_predictions = model.predict(test_mapper)
        node_predictions = target_encoding.inverse_transform(test_predictions)
        results = pd.DataFrame(node_predictions, index=test_nodes).idxmax(axis=1)
        df = pd.DataFrame({'Predicted': results, 'True': test_data[target_feature_name]})
        clean_result_labels = df['Predicted'].map(lambda x: x.replace('subject=', ''))

        # save predicted labels
        pred_labels = np.unique(clean_result_labels.values)
        precision, recall, f1, _ = skmetrics.precision_recall_fscore_support(
            df['True'].values, clean_result_labels.values, average=None, labels=pred_labels
        )
        output_results['classifier'] = []
        for lbl, prec, rec, fm in zip(pred_labels, precision, recall, f1):
            output_results['classifier'].append({'label': lbl, 'precision': prec, 'recall': rec, 'fscore': fm})

        print(output_results['classifier'])
        print(pred_labels)
        print('precision: {}'.format(precision))
        print('recall: {}'.format(recall))
        print('fscore: {}'.format(f1))

        return generator, model, x_inp, x_out, history, target_encoding, output_results
