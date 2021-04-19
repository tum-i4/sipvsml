import argparse
import itertools

import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import confusion_matrix
from torch.utils.data import random_split
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm

from data_loader import read_all_programs_dataset, get_loader, CompositeDataset, TARGET_FLAGS
from model import DeepNN

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default='../data', help='directory for data with programs')
    parser.add_argument('--log_step', type=int, default=10, help='step size for printing training log info')
    parser.add_argument('--debug', type=bool, default=False, help='include additional debugging ifo')
    parser.add_argument('--num_epochs', type=int, default=30)
    parser.add_argument('--regularization', type=float, default=0.001)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--num_workers', type=int, default=2)
    parser.add_argument('--learning_rate', type=float, default=0.00001)
    args = parser.parse_args()
    return args


def print_training_info(batch_accuracy, loss, board_writer, step):
    log_info = '\nTraining - Loss: {:.4f}, Accuracy: {:.4f}'.format(loss.item(), batch_accuracy)
    tqdm.write(log_info)
    board_writer.add_scalar('training loss', loss.item(), step)
    board_writer.add_scalar('training acc', batch_accuracy, step)


def get_detailed_accuracy(all_predictions, all_targets, all_obfuscations):
    # num_examples, 3
    res = []
    for i, obfs in enumerate(all_obfuscations):
        predictions = all_predictions[i]
        targets = all_targets[i]
        for j, flag in enumerate(TARGET_FLAGS):
            res.append({
                'obfs': obfs,
                'flag': flag,
                'prediction': predictions[j].item(),
                'target': targets[j].item()
            })
    return res


def flatten(a_list):
    return list(itertools.chain.from_iterable(a_list))


def print_validation_info(criterion, model, val_loader, epoch, board_writer):
    model.eval()
    with torch.no_grad():
        loss_values = []
        all_predictions = []
        all_targets = []
        all_obfuscations = []
        for features, targets, obfuscations in tqdm(val_loader, desc=f'validation ep. {epoch}'):
            features = features.to(device)
            targets = targets.to(device)

            outputs = model(features)
            loss = calculate_loss(criterion, outputs, targets)
            loss_values.append(loss.item())

            predictions = outputs > 0.0
            all_predictions.append(predictions)
            all_targets.append(targets)
            all_obfuscations.append(obfuscations)

        val_loss = sum(loss_values) / len(loss_values)

        all_predictions = torch.cat(all_predictions).int()
        all_targets = torch.cat(all_targets).int()
        all_obfuscations = flatten(all_obfuscations)
        detailed_accuracy = get_detailed_accuracy(all_predictions, all_targets, all_obfuscations)
        val_accuracy = (all_predictions == all_targets).sum().float().item() / all_predictions.numel()

        tqdm.write('Validation - Loss: {:.3f}, Acc: {:.3f}'.format(val_loss, val_accuracy))
        board_writer.add_scalar('validation loss', val_loss, epoch)
        board_writer.add_scalar('validation acc', val_accuracy, epoch)
    return val_accuracy, detailed_accuracy


def calculate_loss(criteria, outputs, targets):
    return criteria(outputs, targets).mean()


def safe_div(a, b):
    return (a / b) if b != 0 else 0


def save_detailed_results(detailed_results):
    rows = []
    for (obfs, flag), dt in pd.DataFrame(detailed_results).groupby(['obfs', 'flag']):
        y_true, y_pred = dt['target'], dt['prediction']
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        precision = safe_div(tp, (tp + fp))
        recall = safe_div(tp, (tp + fn))
        accuracy = safe_div(tp + tn, tp + tn + fp + fn)
        f1 = safe_div(2 * (precision * recall), (precision + recall))
        rows.append({
            'obfs': obfs,
            'flag': flag,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'accuracy': accuracy
        })
    df = pd.DataFrame(rows)
    df.set_index('obfs').to_csv('best_val_results.csv', encoding='utf-8')
    tqdm.write('\nUpdated best_val_results.csv')


def run_training(args, board_writer):
    all_programs_dataset = read_all_programs_dataset()
    train_size = int(len(all_programs_dataset) * 0.8)
    val_size = len(all_programs_dataset) - train_size
    split = [train_size, val_size]
    train_dataset, val_dataset = random_split(all_programs_dataset, split)
    # Build data loader
    train_loader = get_loader(
        CompositeDataset(*train_dataset), args.batch_size, shuffle=True, num_workers=args.num_workers
    )
    val_loader = get_loader(
        CompositeDataset(*val_dataset), args.batch_size, shuffle=False, num_workers=args.num_workers
    )
    # Device configuration
    tqdm.write(f'training on {device}')
    # Build the models
    model = DeepNN().to(device)
    board_writer.add_text('model', str(model))
    # Loss and optimizer
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(
        model.parameters(), lr=args.learning_rate, weight_decay=args.regularization
    )
    # Train the models
    total_step = len(train_loader)
    step = 1
    top_val_acc = 0.5
    for epoch in range(args.num_epochs):
        iterator = tqdm(enumerate(train_loader), desc=f'training epoch: {epoch}', total=total_step)
        for i, (features, targets, obfuscations) in iterator:
            model.train()

            # Set mini-batch dataset
            features = features.to(device)  # batch_size, 300
            targets = targets.to(device)  # batch_size, 3

            # Forward, backward and optimize
            outputs = model(features)  # batch_size, 3

            loss = calculate_loss(criterion, outputs, targets)
            model.zero_grad()
            loss.backward()
            optimizer.step()

            batch_accuracy = float((outputs > 0.0).eq(targets).sum()) / targets.numel()

            # Print log info
            step += 1

            if (i + 1) % args.log_step == 0:
                print_training_info(batch_accuracy, loss, board_writer, step)

        val_acc, detailed_results = print_validation_info(criterion, model, val_loader, epoch, board_writer)
        if val_acc > top_val_acc:
            top_val_acc = val_acc
            save_detailed_results(detailed_results)


def main():
    args = parse_args()
    board_writer = SummaryWriter()
    board_writer.add_hparams(args.__dict__, {})

    run_training(args, board_writer)

    board_writer.close()


if __name__ == '__main__':
    main()
