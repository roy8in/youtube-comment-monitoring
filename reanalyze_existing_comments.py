import csv
import json
from collections import Counter

from comment_analyzer import analyze_comments_with_llm


def main() -> None:
    with open("dashboard_config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    target_date = config["target_date"]
    prompt_file = f"prompt_{target_date}.txt"
    data_file = f"analyzed_comments_{target_date}.csv"

    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    with open(data_file, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    comments = [row["text"] for row in rows if row.get("text")]
    analyzed_rows = analyze_comments_with_llm(comments, prompt_template)

    final_rows = []
    for index, comment in enumerate(comments):
        analyzed = analyzed_rows[index] if index < len(analyzed_rows) else {}
        final_rows.append(
            {
                "text": comment,
                "sentiment": analyzed.get("sentiment", "오류"),
                "category": analyzed.get("category", "기타"),
                "keyword": analyzed.get("keyword", "누락"),
            }
        )

    with open(data_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "sentiment", "category", "keyword"])
        writer.writeheader()
        writer.writerows(final_rows)

    print(f"re-analyzed {len(final_rows)} comments in {data_file}")
    print("sentiment:", Counter(row["sentiment"] for row in final_rows))
    print("category:", Counter(row["category"] for row in final_rows))


if __name__ == "__main__":
    main()
