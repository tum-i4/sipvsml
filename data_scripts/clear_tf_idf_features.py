from utils import run_with_update_fn


def clean_tf_idf(df):
    df[[f'w_{x}' for x in range(64, 264)]] = 0.0
    return df


def main():
    run_with_update_fn(clean_tf_idf)


if __name__ == '__main__':
    main()
