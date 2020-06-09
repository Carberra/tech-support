import techsupport


def main():
    bot = techsupport.Bot()
    bot.run(techsupport.Config.TOKEN, reconnect=True)


if __name__ == "__main__":
    main()
