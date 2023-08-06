#!/usr/bin/env python

import argparse
import pandas as pd
from termcolor import colored as pc
import warnings
from os import get_terminal_size as tsize
from pandas.core.common import SettingWithCopyWarning
from textwrap import wrap
import os
from re import compile as re_compile
import unidecode
from io import StringIO



_VERSION_ = '1.0'

args_csv="""flags,nargs,action,help,dest,default
-F,1,,[filter] filter (n: new; p: previously asked; h: hidden; a: all),filter,0
-M,1,,[filter] mode (o: ordered; r: random; e: exact answers; E: exact answers if simple; r: review (scores are not stored); u: unforgiving; c: case-sensitive),mode,0
-t,?,,[filter] only include items matching tags,tags,False
-a,1,,[filter] asked before # times,asked,0
-c,1,,[filter] correct before,correct,0
-s,1,,[filter] score [0-10],score,0
-o,1,,[filter] young (<= x days old),young,0
-O,1,,[filter] old (> x days old),old,0
-m,1,,[filter] maximum number of questions to ask,n_max,0
-f,?,,[add   ] filname,filename,False
-π,,store_true,[add   ] new terms (in new.json),new_terms,False
-N,2,,[add   ] term [x] with definition [y],new_term,0
-d,,store_true,[debug ] debug mode,debug,False
-b,,store_true,[debug ] backup database,bk,False
-L,1,,[debug ] list (t: terms; i: information; c: information in csv format; T: tags; s: detailed statistics) & exit,list,0"""

def calc_info(df):
    n_q = df.shape[0]
    n_a = df.n_asked.sum()
    n_c = df.n_correct.sum()
    n_e = (df.index[df.enabled == True]).shape[0]
    n_qa = (df.index[df.n_asked > 0]).shape[0]
    n_qc = (df.index[df.n_correct > 0]).shape[0]
    n_qaq = round(n_a / n_q, 2) if n_q > 0 else 0
    n_qcq = round(n_c / n_q, 2) if n_q > 0 else 0
    n_qca = round(100 * n_c / n_a, 1) if n_a > 0 else 0
    p_a = round(100 * n_qa / n_q, 1) if n_q > 0 else 0
    p_c = round(100 * n_qc / n_q, 1) if n_q > 0 else 0
    return {'n_q': n_q, 'n_a': n_a, 'n_c': n_c, 'n_e': n_e,
            'n_qa': n_qa, 'n_qc': n_qc,
            'n_qaq': n_qaq, 'n_qcq': n_qcq, 'n_qca': n_qca,
            'p_a': p_a, 'p_c': p_c}


def print_info(r, compact=False):
    if compact:
        print(f"{dft['tags'].iloc[0][:4]},"
              + f"{r['n_q']},{r['n_a']},{r['n_qa']},{r['n_qaq']},{r['n_c']},"
              + f"{r['n_qc']},{r['n_qcq']},{r['p_a']},{r['p_c']},{r['n_qca']}")
    else:
        print(f"# terms:\t{r['n_q']}\t[{r['n_e']} enabled]")
        print(f"# asked:\t{r['n_a']}\t[{r['n_qa']} unique]\t"
              + "[%.2f per q]" % r['n_qaq'])
        print(f"# correct:\t{r['n_c']}\t[{r['n_qc']} unique]\t"
              + "[%.2f per q]" % r['n_qcq'])
        print(f"% asked:\t{r['p_a']}%" + "\t%.0f c/a" % r['n_qca'])
        print(f"% correct:\t{r['p_c']}%")


def backup(df):
    from distutils import file_util
    from datetime import datetime
    import sys
    base = "~/.config/study"
    tday = datetime.now().strftime('%y%m%d_%H')
    file_util.copy_file(f"{base}/db.csv", f"{base}/bk_{tday}.csv")
    s_columns = ["n_q", "n_e", "n_qa", "n_qc", "n_a", "n_c",
                 "n_qaq", "n_qcq", "n_qca", "p_a", "p_c"]
    df_stats = pd.DataFrame(columns=s_columns)
    for i in list(range(36)):
        ch = "ch%02i" % i
        dft = df[df.tags.str.lower().str.contains(ch)]
        r = pd.Series(calc_info(dft))
        df_stats.loc[ch] = r
    df_stats.astype(int).to_csv(f"{base}/st_{tday}.csv")
    sys.exit()


def printQ(val, df, args, i, tsize_):
    prescrs = wrap(f"{val['def']}", tsize_ - 30)
    prescr = pc("\n".join(prescrs), "yellow")
    indicator = "⬤"
    postscr0 = indicator
    postscr1 = pc(indicator, "green" if val['enabled'] else "red")
    postscr2 = f"  [{val['tags']}]" \
               + f"   {val['n_asked']}/{df.shape[0] - i}"
    postscr = postscr1 + postscr2
    postscr_plain = postscr0 + postscr2
    eblow_len = tsize_ - (len(prescrs[-1]) % tsize_)

    if args.debug:
        print(f"{eblow_len}, {len(prescrs[-1])},"
              + "{len(postscr_plain)}, {tsize_}")
    sepscr = ""

    if len(postscr_plain) >= eblow_len:
        sepscr = "\n"
        eblow_len = tsize_
    postscr_ = postscr.rjust(eblow_len)
    print(prescr + sepscr + postscr_)

    # if args.sayit:
    #     os.system(f"say \"{val['def']}\"")

    return prescr + sepscr + postscr_


def compare(i, j, exact=False, exactif=False):
    compif = re_compile(r'[^\w \-]')
    if exact:
        return i == j
    elif exactif and not compif.search(j):
        return i == j
    else:
        return i in j


def compareDef(defi, term, exact=False, exactif=False):
    terms = term.split('/')
    for t in terms:
        t = unidecode.unidecode(t)
        if compare(defi, t, exact, exactif):
            return True
    return False


def filter(df, args):
    if args.filter and "h" in args.filter:
        df = df[~df['enabled']]
    elif not (args.filter and "a" in args.filter):
        df = df[df['enabled']]

    if args.tags:
        df = df[df.tags.str.lower().str.contains(args.tags.lower())]

    if args.old or args.young:
        la_diff = (pd.Timestamp.now() - df.last_asked).apply(lambda x: x.days)
        if args.old:
            df = df[la_diff > int(args.old[0])]
        elif args.young:
            df = df[la_diff <= int(args.young[0])]

    if args.filter and "p" in args.filter:
        df = df[df['n_asked'] > 0]
    elif args.filter and "n" in args.filter:
        df = df[df['n_asked'] <= 0]

    if args.asked:
        df = df[df['n_asked'] <= int(args.asked[0])]

    if args.correct:
        df = df[df['n_correct'] <= int(args.correct[0])]

    if args.score:
        score = 10 * df['n_correct'] / df['n_asked']
        score = score.fillna(0)
        df = df[score <= int(args.score[0])]

    # ORDERING
    if not ((args.mode != 0 and "o" in args.mode) or args.list != 0):
        df = df.sample(frac=1, axis=0)
        if not (args.mode != 0 and "r" in args.mode):
            df = df.sort_values(by=['n_correct', 'n_asked'])

    n_max = df.shape[0]

    if args.n_max:
        print(f"maximum: {args.n_max}")
        df = df.iloc[:int(args.n_max[0])]

    # SPECIAL CASES
    if not (args.list or args.new_terms or args.new_term):
        print(f'# QUESTIONS: {df.shape[0]} [out of {n_max} possible]')

    return df


def main():
    tsize_ = None
    warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

    db = '~/.config/study_cli/db.csv'
    jnew = '~/.config/study_cli/new.json'

    argsDF = pd.read_csv(StringIO(args_csv), index_col=0)
    parser = argparse.ArgumentParser(description='Study some more...')
    for argI in argsDF.index:
        arg = argsDF.loc[argI]
        arg = arg.dropna().to_dict()
        if arg.get('nargs') and arg.get('nargs') != '?':
            arg['nargs'] = eval(arg['nargs'])
        arg['default'] = eval(arg['default'])
        parser.add_argument(argI, **arg)

    args = parser.parse_args()
    if args.debug:
        print(args)

    df = pd.read_csv(db, index_col=0)
    df['last_asked'] = df['last_asked'].astype('datetime64')

    # ### ADDING NEW TERMS ### #
    # in the new.json file
    if args.new_terms:
        df0 = pd.read_json(jnew)
        df0 = df0[~df0['def'].isin(df['def'])]
        df = df.append(df0, ignore_index=True, sort=False)

    # from the commandline
    if args.new_term:
        new_term = {"tags": "new", "enabled": True, "n_correct": 0, "n_asked": 0,
                    "term": args.new_term[0],
                    "def": args.new_term[1]}
        df0 = pd.DataFrame([new_term])
        df0 = df0[~df0['def'].isin(df['def'])]
        df = df.append(df0, ignore_index=True, sort=False)

    # from a specified CSV
    if args.filename:
        dfn = pd.read_csv(args.filename)
        dfe = pd.DataFrame(columns=df.columns)
        dfn = pd.concat([dfe, dfn], sort=False)
        dfn['tags'] = dfn['tags'].fillna('')
        dfn['enabled'] = dfn['enabled'].fillna(False)
        dfn['n_asked'] = dfn['n_asked'].fillna(0)
        dfn['n_correct'] = dfn['n_correct'].fillna(0)
        # df = pd.concat([df, dfn], sort=False)
        df = df.append(dfn, ignore_index=True)
        df = df.drop_duplicates(subset=['term', 'def', 'tags'])
        # df.to_csv(db)

    # just backup the current db
    if args.bk:
        backup(df)

    # ### FILTERING ### #
    dfo = df
    df = filter(df, args)

    i = 0
    while i < df.shape[0]:
        if args.list and ("i" in args.list or "I" in args.list):
            dft = dfo if df.shape[0] == 0 else df
            print_info(calc_info(dft))
            break
        elif args.list and "t" in args.list:
            # dft = df[['n_asked', 'n_correct', 'tags', 'term']]
            dft = df[['tags', 'term']]
            # dft['term'] = dft['term'].str.ljust(dft['term'].apply(len).max())
            # print(dft.to_string(index=False, na_rep="-"))
            print(dft.to_csv(None, index=False, na_rep="-"))
            break
        elif args.new_terms or args.new_term or args.filename:
            break

        val = df.loc[df.index[i]]
        id = val.name

        val['n_asked'] = val['n_asked'] + 1
        val_la = val['last_asked']

        if not tsize_:
            tsize_ = tsize().columns

        ques = printQ(val, df, args, i, tsize_)

        wrong = True
        while wrong:
            defi = input("> ")
            term = val['term']
            if defi == "q":
                val['n_asked'] = val['n_asked'] - 1
                wrong = False
            elif defi == "-" or defi == "0" or defi == "\\":
                val['n_asked'] = val['n_asked'] - 1
                val['enabled'] = False
                wrong = False
                print(pc('Question disabled.', 'red'))
            elif defi == "1":
                val['n_asked'] = val['n_asked'] - 1
                val['enabled'] = True
                print(pc(val['term'], 'cyan'))
                wrong = False
                print('This question was just a review.')
            elif defi == "-1":
                df.loc[df.index[i - 1], 'enabled'] = False
                print('Last question was disabled.')
            elif defi == "k":
                os.system('clear')
                print(ques)
            elif defi == "r":
                df.loc[df.index[i - 1],
                       'n_asked'] = df.loc[df.index[i - 1],
                                           'n_asked'] - 1
                print('Last question was just a review.')
            elif len(defi) == 0:
                val_la = pd.Timestamp.today()
                print(pc(val['term'], "blue"))
                wrong = False
            else:
                if not (args.mode and "c" in args.mode):
                    defi = defi.lower()
                    term = term.lower()
                comp = compareDef(defi, term, (args.mode and "e" in args.mode), (args.mode and "E" in args.mode))
                if args.debug:
                    print(f'args.exact: {(args.mode and "e" in args.mode)}, args.exactif: {(args.mode and "E" in args.mode)}, comparison result: {comp}')
                if comp:
                    val['n_correct'] = val['n_correct'] + 1
                    val_la = pd.Timestamp.today()
                    postscr = f" [{val['n_correct']}/{val['n_asked']}]" + \
                              f" It is {val['term']}"
                    print(pc("Correct!", "green"), postscr)
                    # if args.sayit:
                    #     os.system(f"say correct")
                    wrong = False
                else:
                    val_la = pd.Timestamp.today()
                    print(pc("Incorrect!", "red") +
                          f" [{val['n_correct']}/{val['n_asked']}]")
                    if (args.mode and "u" in args.mode):
                        print("\tthat was..." +
                              pc(val['term'], "red"))
                        # if args.sayit:
                        #     os.system(f"say incorrect")
                        #     os.system(f"say \"correct answer is {val['term']}\"")
                        wrong = False
        if (args.mode and "r" in args.mode):
            val['n_asked'] = val['n_asked'] - 1
        else:
            val['last_asked'] = val_la

        df.loc[val.name] = val
        if defi == "q":
            break
        i = i + 1

    dfo.loc[df.index] = df.loc[df.index]
    dfo.to_csv(db)

if __name__ == '__main__':
    main()
