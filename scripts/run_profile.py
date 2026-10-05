from profiling.profile_data import generate_profile

if __name__ == "__main__":
    generate_profile(
        "data/raw/netflix_titles.csv",
        "data/profiling/netflix_profile.html",
    )
