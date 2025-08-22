from pyrogram import *
from pyrogram.types import *
import aiohttp
import asyncio
from TG_API_TOKENS import API_ID, API_HASH
from ID_TG_CHATS import ID_CHAT


htmlChecker = Client("htmlChecker", API_ID, API_HASH)

global flagStartCheck
flagStartCheck = False

async def getLikes():
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://testdrive.urfu.ru/presentations/327/') as response:
            html = await response.text()

            ind = html.find("item likes") + len("item likes") + 8

            text = ""
            for i in range(ind, ind+3):
                text += html[i]
            return text

async def getAllTeams():
    teams = []

    async with aiohttp.ClientSession() as session:
        for i in range(1, 10000):
            async with session.get(f'https://testdrive.urfu.ru/presentations/{i}/') as response:
                try:
                    html = await response.text()
                    if (html == "<h1>Not Found</h1><p>The requested resource was not found on this server.</p>"):
                        break


                    ind = html.find("data-team-id=") + len("data-team-id=") + 1
                    id = "".join([html[j] for j in range(ind, ind+4) if html[j] in "0123456789"])

                    ind = html.find("item likes") + len("item likes") + 8
                    likes = "".join([html[j] for j in range(ind, ind+4) if html[j] in "0123456789"])

                    ind = html.find("title") + len("title") + 2
                    title = ""
                    for j in range(ind, ind+777):
                        if (html[j] == "<" and html[j+1] == "/"):
                            break
                        title += html[j]
                    title = title.replace("&quot;", "'")

                    if (title != "None"):
                        teams.append([id, likes, title])
                except:
                    break
    return teams

async def checkHtmlResponse():
    async with aiohttp.ClientSession() as session:
        while (flagStartCheck):
            async with session.get(f'https://testdrive.urfu.ru/rating/scores/') as response:
                html = await response.text()

                with open("C:\\Users\\Матвей\\project\\urfuTgBot\\htmlResponse.txt", "r", encoding="UTF-8") as file: # /root/pythonProjects/urfuTgBot/htmlResponse.txt
                    if (html != file.read()):
                        await htmlChecker.send_message(ID_CHAT, "Что-то происходит")
            await asyncio.sleep(60)


@htmlChecker.on_message()
async def startCheck(client: Client, message: Message):
    global flagStartCheck

    if (message.chat.id == ID_CHAT):
        # Запуск проверки
        if (message.text == "!Запуск проверки"):
            if (flagStartCheck == True):
                await message.reply_text("Проверка уже запущена", True)

            if (flagStartCheck == False):
                flagStartCheck = True
                asyncio.create_task(checkHtmlResponse())
                await message.reply_text("Проверка запущена", True)
        

        # Остановка проверки
        if (message.text == "!Остановка проверки"):
            if (flagStartCheck == False):
                await message.reply_text("Проверка уже остановлена", True)
                return
            
            if (flagStartCheck == True):
                flagStartCheck = False
                asyncio.create_task(checkHtmlResponse())
                await message.reply_text("Проверка остановлена", True)
                return


        # Кол-во лайков
        if (message.text == "!лайки"):
            taskGetLikes = asyncio.create_task(getLikes())
            likes = await taskGetLikes

            await message.reply_text(f"Всего {likes} лайков")


        # Место или топ
        if (message.text == "!место" or message.text == "!топ"):
            await message.reply_text("Подождите пару минут...")

            taskGetAllTeams = asyncio.create_task(getAllTeams())
            teams = await taskGetAllTeams

            for i in range(len(teams)-1):
                for j in range(len(teams)-1-i):
                    if int(teams[j][1]) > int(teams[j+1][1]):
                        teams[j][1], teams[j+1][1] = teams[j+1][1], teams[j][1]
                        teams[j][0], teams[j+1][0] = teams[j+1][0], teams[j][0]
                        teams[j][2], teams[j+1][2] = teams[j+1][2], teams[j][2]


            # Топ
            if (message.text == "!топ"):
                topTeams = ""

                topTeams += "Место Название Лайки id\n====>\n"
                for i in range(len(teams)-1, len(teams)-1-10, -1):
                    topTeams += f"{len(teams)-i} {teams[i][2]} {teams[i][1]} {teams[i][0]}\n"
                topTeams += "====>\n"

                for i in range(len(teams)):
                    if (teams[i][2] == "Инженеры (демо-версия)"):
                        topTeams += f"{len(teams)-i-1} {teams[i+1][2]} {teams[i+1][1]} {teams[i+1][0]}\n"
                        topTeams += f"{len(teams)-i} {teams[i][2]} {teams[i][1]} {teams[i][0]}\n"
                        topTeams += f"{len(teams)-i+1} {teams[i-1][2]} {teams[i-1][1]} {teams[i-1][0]}"
                        break

                await message.reply_text(topTeams)
            
            
            # Место
            if (message.text == "!место"):
                for i in range(len(teams)):
                    if (teams[i][2] == "Инженеры (демо-версия)"):
                        await message.reply_text(f"{len(teams)-i} место из {len(teams)}")
                        break

htmlChecker.run()
