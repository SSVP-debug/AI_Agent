# main.py
from core.orchestrator import run_pipeline

def main():
    topic = input("Enter business idea theme: ").strip()
    if not topic:
        print("Please provide a topic.")
        return
    print("[Running pipeline — this may take a few seconds depending on the model]")
    final = run_pipeline(topic)
    print("\n\n===== FINAL BUSINESS BLUEPRINT =====\n")
    print(final)
    with open("final_business_blueprint.txt", "w", encoding="utf-8") as f:
        f.write(final)
    print("\nSaved as final_business_blueprint.txt")

if __name__ == "__main__":
    main()
