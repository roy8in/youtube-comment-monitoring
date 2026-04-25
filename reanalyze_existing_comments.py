import argparse
import csv
from collections import Counter

from comment_analyzer import analyze_comments_with_llm, normalize_sentiment_label
from config_loader import (
    data_file_for_report,
    get_default_report,
    get_report_by_id,
    load_dashboard_config,
    resolve_prompt_file,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="기존 댓글 CSV를 다시 분석합니다.")
    parser.add_argument("--report-id", help="dashboard_config.json의 report id")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_dashboard_config()
    report = get_report_by_id(config, args.report_id) if args.report_id else get_default_report(config)
    if not report:
        raise ValueError("재분석할 report를 찾지 못했습니다.")

    prompt_file = resolve_prompt_file(report, config)
    data_file = data_file_for_report(report)

    with open(prompt_file, "r", encoding="utf-8") as file:
        prompt_template = file.read()

    with open(data_file, "r", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    comments = [row["text"] for row in rows if row.get("text")]
    analyzed_rows = analyze_comments_with_llm(comments, prompt_template)

    final_rows = []
    for index, comment in enumerate(comments):
        analyzed = analyzed_rows[index] if index < len(analyzed_rows) else {}
        final_rows.append(
            {
                "text": comment,
                "sentiment": normalize_sentiment_label(analyzed.get("sentiment", "오류")),
                "category": analyzed.get("category", "기타"),
                "keyword": analyzed.get("keyword", "누락"),
            }
        )

    with open(data_file, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["text", "sentiment", "category", "keyword"])
        writer.writeheader()
        writer.writerows(final_rows)

    print(f"re-analyzed {len(final_rows)} comments in {data_file} ({report.get('id')})")
    print("sentiment:", Counter(row["sentiment"] for row in final_rows))
    print("category:", Counter(row["category"] for row in final_rows))


if __name__ == "__main__":
    main()
