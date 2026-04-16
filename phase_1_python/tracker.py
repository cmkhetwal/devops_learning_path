#!/usr/bin/env python3
"""
DevOps Python Learning Path - Progress Tracker
Run this daily to log your progress and see stats.
Usage: python3 tracker.py
"""

import json
import os
from datetime import datetime, timedelta

PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "progress", "progress.json")
TOTAL_WEEKS = 12
DAYS_PER_WEEK = 7
TOTAL_DAYS = TOTAL_WEEKS * DAYS_PER_WEEK


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {
        "start_date": None,
        "days_completed": {},
        "quiz_scores": {},
        "streaks": {"current": 0, "longest": 0, "last_date": None},
        "notes": {},
    }


def save_progress(data):
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_current_day(progress):
    completed = progress["days_completed"]
    for w in range(1, TOTAL_WEEKS + 1):
        for d in range(1, DAYS_PER_WEEK + 1):
            key = f"w{w:02d}d{d}"
            if key not in completed:
                return w, d
    return TOTAL_WEEKS, DAYS_PER_WEEK


def update_streak(progress):
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    last = progress["streaks"]["last_date"]

    if last == today:
        return  # Already logged today

    if last == yesterday:
        progress["streaks"]["current"] += 1
    else:
        progress["streaks"]["current"] = 1

    progress["streaks"]["last_date"] = today
    if progress["streaks"]["current"] > progress["streaks"]["longest"]:
        progress["streaks"]["longest"] = progress["streaks"]["current"]


def display_progress_bar(completed, total, width=40):
    filled = int(width * completed / total) if total > 0 else 0
    bar = "█" * filled + "░" * (width - filled)
    pct = (completed / total * 100) if total > 0 else 0
    return f"[{bar}] {pct:.1f}%"


def display_dashboard(progress):
    completed_count = len(progress["days_completed"])
    week, day = get_current_day(progress)

    print("\n" + "=" * 60)
    print("   PYTHON FOR DEVOPS - PROGRESS DASHBOARD")
    print("=" * 60)

    # Current position
    phase = "Phase 1: Fundamentals" if week <= 4 else "Phase 2: Intermediate + DevOps" if week <= 8 else "Phase 3: Cloud & DevOps"
    print(f"\n  Current Position: Week {week}, Day {day}")
    print(f"  Current Phase:    {phase}")

    # Overall progress
    print(f"\n  Overall Progress:")
    print(f"  {display_progress_bar(completed_count, TOTAL_DAYS)}")
    print(f"  {completed_count}/{TOTAL_DAYS} days completed")

    # Phase progress
    print(f"\n  Phase Progress:")
    p1 = sum(1 for k in progress["days_completed"] if int(k[1:3]) <= 4)
    p2 = sum(1 for k in progress["days_completed"] if 5 <= int(k[1:3]) <= 8)
    p3 = sum(1 for k in progress["days_completed"] if int(k[1:3]) >= 9)
    print(f"  Phase 1 (Basics):  {display_progress_bar(p1, 28)}")
    print(f"  Phase 2 (DevOps):  {display_progress_bar(p2, 28)}")
    print(f"  Phase 3 (Cloud):   {display_progress_bar(p3, 28)}")

    # Streak
    streak = progress["streaks"]
    print(f"\n  Streaks:")
    fire = "🔥" if streak["current"] >= 3 else "  "
    print(f"  Current Streak: {streak['current']} days {fire}")
    print(f"  Longest Streak: {streak['longest']} days")

    # Quiz scores
    if progress["quiz_scores"]:
        print(f"\n  Quiz Scores:")
        for week_num, score in sorted(progress["quiz_scores"].items()):
            grade = "Excellent!" if score >= 90 else "Good" if score >= 70 else "Review needed" if score >= 50 else "Retry recommended"
            bar = "█" * (score // 10) + "░" * (10 - score // 10)
            print(f"  Week {week_num:>2}: [{bar}] {score}% - {grade}")

        avg = sum(progress["quiz_scores"].values()) / len(progress["quiz_scores"])
        print(f"\n  Average Score: {avg:.1f}%")
    else:
        print(f"\n  No quiz scores yet. Take your first quiz: python3 quiz.py 1")

    # Motivation
    print(f"\n  {'─' * 50}")
    if completed_count == 0:
        print("  Welcome! Let's start your DevOps Python journey!")
        print("  Begin with: cat week_01/day_1/lesson.md")
    elif completed_count < 28:
        print("  Keep going! You're building a solid foundation.")
    elif completed_count < 56:
        print("  Great progress! You're getting into real DevOps work.")
    elif completed_count < 84:
        print("  Amazing! You're building cloud-level skills now!")
    else:
        print("  YOU DID IT! You've completed the entire program!")
    print("=" * 60 + "\n")


def mark_day_complete(progress):
    week, day = get_current_day(progress)
    key = f"w{week:02d}d{day}"

    if key in progress["days_completed"]:
        print(f"\n  Day already completed!")
        return

    print(f"\n  Ready to mark Week {week}, Day {day} as complete?")
    print(f"  Topic: Check the lesson file for today's topic.")

    # Self-assessment
    print(f"\n  How confident do you feel about today's topic?")
    print(f"  1 = Not confident, need to review")
    print(f"  2 = Somewhat confident")
    print(f"  3 = Confident, understood well")
    print(f"  4 = Very confident, could teach it")

    while True:
        try:
            confidence = int(input("\n  Your rating (1-4): "))
            if 1 <= confidence <= 4:
                break
            print("  Please enter 1, 2, 3, or 4")
        except ValueError:
            print("  Please enter a number")
        except (EOFError, KeyboardInterrupt):
            print("\n  Cancelled.")
            return

    # Optional notes
    try:
        note = input("  Any notes for today? (press Enter to skip): ").strip()
    except (EOFError, KeyboardInterrupt):
        note = ""

    progress["days_completed"][key] = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "confidence": confidence,
    }

    if note:
        progress["notes"][key] = note

    if progress["start_date"] is None:
        progress["start_date"] = datetime.now().strftime("%Y-%m-%d")

    update_streak(progress)
    save_progress(progress)

    print(f"\n  Day {day} of Week {week} marked complete!")

    # Check if exercise was done
    exercise_path = os.path.join(
        os.path.dirname(__file__), f"week_{week:02d}", f"day_{day}", "exercise.py"
    )
    check_path = os.path.join(
        os.path.dirname(__file__), f"week_{week:02d}", f"day_{day}", "check.py"
    )

    if os.path.exists(check_path):
        print(f"  Don't forget to verify: python3 week_{week:02d}/day_{day}/check.py")

    # Low confidence warning
    if confidence <= 2:
        print(f"\n  Tip: Since you rated confidence low, consider:")
        print(f"  - Re-reading the lesson tomorrow before moving on")
        print(f"  - Trying the exercise again from scratch")
        print(f"  - Searching YouTube for '{get_topic_hint(week, day)}' tutorials")


def get_topic_hint(week, day):
    topics = {
        (1, 1): "python hello world tutorial",
        (1, 2): "python variables and data types",
        (1, 3): "python input output beginner",
        (1, 4): "python math operations",
        (1, 5): "python strings tutorial",
        (2, 1): "python if else tutorial",
        (2, 3): "python while loops",
        (2, 4): "python for loops",
        (3, 1): "python lists tutorial",
        (3, 4): "python dictionaries tutorial",
        (4, 1): "python functions tutorial",
        (5, 3): "python json yaml parsing",
        (6, 2): "python subprocess tutorial",
        (7, 2): "python requests library",
    }
    return topics.get((week, day), "python beginner tutorial")


def show_weak_areas(progress):
    low_confidence = []
    for key, data in progress["days_completed"].items():
        if data.get("confidence", 3) <= 2:
            week = int(key[1:3])
            day = int(key[-1])
            low_confidence.append((week, day, data["confidence"]))

    if low_confidence:
        print("\n  Areas to Review (low confidence ratings):")
        for week, day, conf in low_confidence:
            print(f"  - Week {week}, Day {day} (confidence: {conf}/4)")
            print(f"    Review: cat week_{week:02d}/day_{day}/lesson.md")
    else:
        print("\n  No weak areas detected! Great confidence across the board.")


def main():
    progress = load_progress()

    print("\n  What would you like to do?")
    print("  1. View Dashboard")
    print("  2. Mark Today's Lesson Complete")
    print("  3. View Weak Areas (topics to review)")
    print("  4. View Study Notes")
    print("  5. Reset Progress (start over)")

    try:
        choice = input("\n  Choose (1-5): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if choice == "1":
        display_dashboard(progress)
    elif choice == "2":
        mark_day_complete(progress)
        display_dashboard(progress)
    elif choice == "3":
        show_weak_areas(progress)
    elif choice == "4":
        if progress["notes"]:
            print("\n  Your Study Notes:")
            for key, note in progress["notes"].items():
                week = int(key[1:3])
                day = int(key[-1])
                print(f"  Week {week}, Day {day}: {note}")
        else:
            print("\n  No notes yet. Add notes when marking days complete.")
    elif choice == "5":
        try:
            confirm = input("  Are you sure? Type 'yes' to reset: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Cancelled.")
            return
        if confirm.lower() == "yes":
            save_progress({
                "start_date": None,
                "days_completed": {},
                "quiz_scores": {},
                "streaks": {"current": 0, "longest": 0, "last_date": None},
                "notes": {},
            })
            print("  Progress reset!")
    else:
        print("  Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main()
