import argparse
import json
from pathlib import Path
import pandas as pd


def detect_label_column(df):
    candidates = [c for c in df.columns if 'label' in c.lower() or c.lower() == 'label' or c.lower() == 'sentiment']
    return candidates[0] if candidates else None


def summarize_df(df, name, sample_n=5):
    cols = list(df.columns)
    dtypes = {c: str(df[c].dtype) for c in cols}
    nulls = {c: int(df[c].isna().sum()) for c in cols}
    samples = {c: df[c].dropna().astype(str).head(sample_n).tolist() for c in cols}
    return {'name': name, 'n_rows': int(len(df)), 'columns': cols, 'dtypes': dtypes, 'nulls': nulls, 'samples': samples}


def compare_summaries(col_sum, proc_sum):
    col_set = set(col_sum['columns'])
    proc_set = set(proc_sum['columns'])
    only_in_collected = sorted(list(col_set - proc_set))
    only_in_processed = sorted(list(proc_set - col_set))
    common = sorted(list(col_set & proc_set))
    return {
        'only_in_collected': only_in_collected,
        'only_in_processed': only_in_processed,
        'common_columns': common,
        'collected_rows': col_sum['n_rows'],
        'processed_rows': proc_sum['n_rows'],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--collected', default='data/collected/apify_facebook_comments_preprocessed.csv')
    p.add_argument('--processed', default='data/processed/train.csv')
    p.add_argument('--out', default='reports/results/compare_apify_vs_processed.json')
    args = p.parse_args()

    collected_path = Path(args.collected)
    processed_path = Path(args.processed)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not collected_path.exists():
        print(f'Collected file not found: {collected_path}')
        return
    if not processed_path.exists():
        print(f'Processed file not found: {processed_path}')
        return

    col_df = pd.read_csv(collected_path)
    proc_df = pd.read_csv(processed_path)

    col_sum = summarize_df(col_df, 'collected')
    proc_sum = summarize_df(proc_df, 'processed')

    comp = compare_summaries(col_sum, proc_sum)

    # Check cleaned_text presence
    cleaned_in_collected = 'cleaned_text' in col_df.columns
    cleaned_in_processed = 'cleaned_text' in proc_df.columns

    # Detect label column in processed
    label_col = detect_label_column(proc_df)
    label_distribution = None
    if label_col:
        label_distribution = proc_df[label_col].value_counts(dropna=False).to_dict()

    report = {
        'collected_summary': col_sum,
        'processed_summary': proc_sum,
        'comparison': comp,
        'cleaned_text': {
            'in_collected': cleaned_in_collected,
            'in_processed': cleaned_in_processed,
        },
        'processed_label_column': label_col,
        'processed_label_distribution': label_distribution,
    }

    with out_path.open('w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print('Wrote comparison report to', out_path)


if __name__ == '__main__':
    main()
