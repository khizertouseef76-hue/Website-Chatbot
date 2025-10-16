# run_chatbot.py
import subprocess, argparse, os, sys

def run(cmd):
    print(f"\n>>> Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        sys.exit(result.returncode)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", nargs="*")
    parser.add_argument("--sitemap")
    args = parser.parse_args()

    # 1. Scrape
    scrape_cmd = "python -m src.scraper_dynamic"
    if args.sitemap:
        scrape_cmd += f" --sitemap {args.sitemap}"
    if args.urls:
        scrape_cmd += " --urls " + " ".join(args.urls)
    run(scrape_cmd)

    # 2. Build Index
    run("python -m src.build_index --infile data/chunks.jsonl")

    # 3. Launch UI
    run("streamlit run app.py")

if __name__ == "__main__":
    main()