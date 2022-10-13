"""wordle 猜单词游戏
.wdstart 开始新的个人游戏
.wd [单词] 尝试猜单词
没有正在进行的游戏的情况下，直接使用 .wd 则默认开启新游戏并马上进行第一次猜测。
"""

from EAbotoy.collection import MsgTypes
from EAbotoy.decorators import ignore_botself, startswith, these_msgtypes
from EAbotoy.model import WeChatMsg
from EAbotoy import sugar
import random
import re


def load_wordlist(filename):
    wordlist_file = open(filename)
    wordlist_lines = wordlist_file.readlines()
    wordlist_file.close()
    lst = list(map(lambda l: l.split(" ", 1), filter(lambda l: len(l) >= 1 and l[0][0] != "#",
                                                     [line.strip().lower() for line in
                                                      wordlist_lines])))  # split into [word,translation]s
    return {x[0]: (x[1] if len(x) > 1 else "") for x in lst}


WORDLE_WORD_LIST = "./resources/wordle_words.txt"  # 所有可作为输入接受的单词列表
WORDLE_ANSWER_LIST = "./resources/wordle_answers.txt"  # 所有可能生成的答案单词，必须是 wordle_word 的子集

wordlist = load_wordlist(WORDLE_WORD_LIST)
answerlist = list(load_wordlist(WORDLE_ANSWER_LIST).keys())


def wordlecore_match(correct_word, guess):
    correct = list(correct_word)
    result = list("@" * len(correct_word))
    for i, v in enumerate(guess):
        if correct[i] == v:
            result[i] = 'O'
            correct[i] = ' '

    for i, v in enumerate(guess):
        if result[i] != '@':
            continue
        try:
            matchpos = correct.index(v)
            result[i] = '?'
            correct[matchpos] = ' '
        except ValueError:
            result[i] = '_'
    return ''.join(result)


sessions = {}


def wd_start_personal(wxid):
    correct_word = answerlist[random.randrange(0, len(answerlist))]
    print("DEBUG:", correct_word)
    sessions[wxid] = {
        "correct_word": correct_word,
        "previous_guesses": [],
        "total_guesses_allowed": 5,
        "win": False,
    }
    return sessions[wxid]


def wd_get_session(wxid):
    return sessions.get(wxid)


def wd_gameover(session):
    return session["win"] or len(session["previous_guesses"]) >= session["total_guesses_allowed"]


def wd_stopsession(wxid):
    sessions.pop(wxid)


def wd_make_guess(session, guess_word):
    session["previous_guesses"].append(guess_word)


def prompt_new_game(session):
    return "开始新的猜词游戏，单词长度为 {}，你共有 {} 次猜测机会".format(len(session["correct_word"]),
                                                                        session["total_guesses_allowed"])


def prompt_word_trans(format, word):
    wordtrans = wordlist.get(word.lower())
    if wordtrans is not None and len(wordtrans) > 1 and len(wordtrans[1].strip()) > 0:
        return format.format(wordtrans.strip())
    return ""


def prompt_guess_history(session):
    res = []
    guesses = session["previous_guesses"]
    correct_word = session["correct_word"]
    for word in guesses:
        result = wordlecore_match(correct_word, word)
        res.append("   ".join(list(word.upper())) + "\n" + result.replace('_', '⬜').replace('O', '🟩').replace('?',
                                                                                                              '🟨') + prompt_word_trans(
            "  {}", word))

    return '\n'.join(res)


def wd_check_game_win(session):
    guesses = session["previous_guesses"]
    correct_word = session["correct_word"]
    if guesses[-1] == correct_word:
        session["win"] = True
        if len(guesses) == 1:
            return "恭喜你（逆天地）在第 1 发就猜中了正确单词 {}！{}".format(correct_word.upper(),
                                                                          prompt_word_trans("单词释义：{}",
                                                                                            correct_word))
        else:
            return "恭喜你在第 {} 发猜中正确单词 {}！{}".format(len(guesses), correct_word.upper(),
                                                               prompt_word_trans("单词释义：{}", correct_word))
    elif wd_gameover(session):
        return "游戏结束，正确单词为 " + correct_word + prompt_word_trans("（{}）", correct_word)
    else:
        return "还有 {} 次机会".format(session["total_guesses_allowed"] - len(guesses))


@ignore_botself
@these_msgtypes(MsgTypes.TextMsg)
@startswith(".wd")
def receive_wx_msg(ctx: WeChatMsg):
    wxid = ctx.FromUserName

    if ctx.Content == ".wdstart":
        session = wd_start_personal(wxid)
        print(
            prompt_new_game(session) + "，使用 .wd [单词] 开始猜词",
            True, ctx
        )
        return

    guess_word = ctx.Content.split(' ')[-1].lower()
    if re.match('^[a-z]+$', guess_word) is None:
        print("无效单词，必须为纯字母", True, ctx)
        return

    is_new_game = False
    session = wd_get_session(wxid)
    if session is None:
        session = wd_start_personal(wxid)
        is_new_game = True

    correct_length = len(session["correct_word"])
    if len(guess_word) != correct_length:
        print("长度错误！请输入 {} 字母长的单词".format(correct_length), True, ctx)
        return

    if wordlist.get(guess_word) is None:
        print("无效单词，'{}' 不在单词表中".format(guess_word), True, ctx)
        return

    wd_make_guess(session, guess_word)

    if is_new_game:
        print(prompt_new_game(session) + "，你的第一个猜测结果：\n" + prompt_guess_history(
            session) + "\n" + wd_check_game_win(session), True, ctx)
    else:
        print("\n" + prompt_guess_history(session) + "\n" + wd_check_game_win(session), True, ctx)

    if wd_gameover(session):
        wd_stopsession(wxid)
