from playwright.sync_api import sync_playwright, expect
from kickstarter import run, run2  # 假设 kickstarter.py 在上一级目录

expected_locations = [
    "Los Angeles, CA",
    "Seattle, WA",
    "Chicago, IL",
    "New York, NY",
    "Houston, TX"
]

def test_location_extraction():
    with sync_playwright() as playwright:
        initial_url = "https://www.kickstarter.com/projects/metismediarpg/astra-arcanum-the-roleplaying-game/community"
        href_list = run(playwright, initial_url)
        actual_locations = run2(playwright, href_list)
        print(actual_locations)
        assert sorted(actual_locations) == sorted(expected_locations)