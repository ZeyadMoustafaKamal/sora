from anime import Anime

def main():
    url = "https://witanime.quest/episode/ao-no-hako-%d8%a7%d9%84%d8%ad%d9%84%d9%82%d8%a9-6/"
    anime = Anime(url)
    episodes_line = "12-17"
    anime.download(episodes_line)

if __name__ == "__main__":
    main()
