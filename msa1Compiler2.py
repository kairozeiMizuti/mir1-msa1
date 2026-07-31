#mir1Code.csvをprogram.csvに変換します
#program.csvはROM_writer.pyで樽データに変換可能です

import csv

#デバッグ情報がprintされます
debugging = False

#mir1をチャンク単位で分割する
def chunk_split(code):
    chunks = []
    code_chunk = []
    for i in range(len(code)):
        code_chunk.append(code[i])
        if i == len(code) - 1:
            chunks.append(code_chunk)
        elif "func" in code[i + 1] or "return" in code[i]:
            chunks.append(code_chunk)
            code_chunk = []
    return chunks

#mir1のチャンクをブロック単位で分割する
def block_split(code):
    blocks = []
    code_block = []
    for i in range(len(code)):
        code_block.append(code[i])
        if i == len(code) - 1:
            blocks.append(code_block)
        elif "jump" in code[i] or "if" in code[i] or "call" in code[i]:
            blocks.append(code_block)
            code_block = []
        elif "label" in code[i + 1] or "func" in code[i + 1]:
            blocks.append(code_block)
            code_block = []
    return blocks


#命令別の使用されるレジスタを返す
#引数チェックも兼ねている
def use_regiister(instruction):
    if instruction[0] == "move":
        if len(instruction) != 3:
            print("move命令の引数がおかしいです")
            exit()
        if "r" in instruction[2]:
            return [instruction[1], instruction[2]]
        return [instruction[1]]
    elif instruction[0] == "add":
        if len(instruction) != 4:
            print("add命令の引数がおかしいです")
            exit()
        if "r" in instruction[3]:
            return [instruction[1], instruction[2], instruction[3]]
        return [instruction[1], instruction[2]]
    elif instruction[0] == "sub":
        if len(instruction) != 4:
            print("sub命令の引数がおかしいです")
            exit()
        if "r" in instruction[3]:
            return [instruction[1], instruction[2], instruction[3]]
        return [instruction[1], instruction[2]]
    elif instruction[0] == "if":
        if len(instruction) != 5:
            print("if命令の引数がおかしいです")
            exit()
        if "r" in instruction[3]:
            return [instruction[2], instruction[3]]
        return [instruction[2]]
    elif instruction[0] == "input":
        if len(instruction) != 3:
            print("input命令の引数がおかしいです")
            exit()
        return [instruction[1]]
    elif instruction[0] == "output":
        if len(instruction) != 3:
            print("output命令の引数がおかしいです")
            exit()
        if "r" in instruction[2]:
            return [instruction[2]]
    elif instruction[0] == "mullo":
        if len(instruction) != 4:
            print("mullo命令の引数がおかしいです")
            exit()
        if "r" in instruction[3]:
            return [instruction[1], instruction[2], instruction[3]]
        return [instruction[1], instruction[2]]
    elif instruction[0] == "mulhi":
        if len(instruction) != 4:
            print("mulhi命令の引数がおかしいです")
            exit()
        if "r" in instruction[3]:
            return [instruction[1], instruction[2], instruction[3]]
        return [instruction[1], instruction[2]]
    elif instruction[0] == "div":
        if len(instruction) != 4:
            print("div命令の引数がおかしいです")
            exit()
        if "r" in instruction[3]:
            return [instruction[1], instruction[2], instruction[3]]
        return [instruction[1], instruction[2]]
    elif instruction[0] == "mod":
        if len(instruction) != 4:
            print("mod命令の引数がおかしいです")
            exit()
        if "r" in instruction[3]:
            return [instruction[1], instruction[2], instruction[3]]
        return [instruction[1], instruction[2]]
    elif instruction[0] == "rishift":
        if len(instruction) != 4:
            print("rishift命令の引数がおかしいです")
            exit()
        return [instruction[1], instruction[2]]


#次使う順を返す
def register0(code, index, register):
    #優先度0は今後使用されないレジスタという意味
    yuusendo = [0 for _ in range(len(register))]
    #ゼロレジスタは常に書き換えないようにする
    yuusendo[0] = 16
    #次の優先度番号
    count = 15
    for i in range(index, len(code)):
        use_reg = use_regiister(code[i])
        if use_reg == None:
            continue
        for j in range(len(register)):
            if register[j] in use_reg and yuusendo[j] == 0:
                yuusendo[j] = count
                count -= 1
    return yuusendo

#今後使う回数を返す
def register1(code, index, register):
    #優先度0は今後使用されないレジスタという意味
    yuusendo = [0 for _ in range(len(register))]
    for i in range(index, len(code)):
        #ゼロレジスタは常に書き換えないようにする
        yuusendo[0] += 3
        if i == index:
            continue
        use_reg = use_regiister(code[i])
        if use_reg == None:
            continue
        for j in range(len(register)):
            if register[j] in use_reg:
                yuusendo[j] += 1
    return yuusendo


#レジスタの配置を決定する(アルゴリズム0)
def register_list0(code, index, register):
    add_registers = []
    use_reg = use_regiister(code[index])
    if use_reg == None:
        return register
    for i in use_reg:
        add = True
        for j in register:
            if j == i or i in add_registers:
                add = False
        if add:
            add_registers.append(i)

    reg0 = register0(code, index, register)

    # 最小の値とそのインデックスを求める
    min_values_with_indices = sorted(enumerate(reg0), key=lambda x: (x[1], x[0]))
    # 結果の取得
    indices = [index for index, value in min_values_with_indices]

    for i in range(len(add_registers)):
        register[indices[i]] = add_registers[i]

    return register

#レジスタの配置を決定する(アルゴリズム1)
def register_list1(code, index, register):
    add_registers = []
    use_reg = use_regiister(code[index])
    if use_reg == None:
        return register
    for i in use_reg:
        add = True
        for j in register:
            if j == i or i in add_registers:
                add = False
        if add:
            add_registers.append(i)

    reg1 = register1(code, index, register)

    # 最小の値とそのインデックスを求める
    min_values_with_indices = sorted(enumerate(reg1), key=lambda x: (x[1], x[0]))
    # 結果の取得
    indices = [index for index, value in min_values_with_indices]

    for i in range(len(add_registers)):
        register[indices[i]] = add_registers[i]

    return register


#レジスタ変更回数をカウントする
def register_list_change_count(register_list):
    score = 0
    if len(register_list) < 2:
        return score
    for i in range(1, len(register_list)):
        for j in range(len(register_list[i - 1])):
            if register_list[i - 1][j] != register_list[i][j]:
                score += 1
    return score



#レジスタ割り当てを最初まで引き延ばす
def register_init(register_list):
    if len(register_list) < 2:
        return register_list
    for i in range(1, len(register_list)):
        j = 0 - i
        for k in range(15):
            if register_list[j - 1][k] == "0":
                register_list[j - 1][k] = register_list[j][k]
    return register_list



#レジスタ割り当ての最初と最後に別ブロックとの通信を考慮した割り当てを追加する
#チャンク別に行う
def register_add_communication(code, register_list):
    #ブロックの繋がりを辞書に入れる
    block_conect = {"in": [], "out": [], "first": [], "last": []}
    #自分のブロックからどのブロックに向かうかを調べる
    for i in range(len(code)):
        conect_out = []
        if code[i][-1][0] == "jump":
            for j in range(len(code)):
                if code[j][0][0] == "label" and code[j][0][1] == code[i][-1][1]:
                    conect_out.append(j)
        elif code[i][-1][0] == "if":
            for j in range(len(code)):
                if code[j][0][0] == "label" and code[j][0][1] == code[i][-1][4]:
                    conect_out.append(j)
        elif code[i][-1][0] == "return":
            conect_out.append("func")
        elif code[i][-1][0] == "call":
            conect_out.append("func")
        if i + 1 != len(code):
            conect_out.append(i + 1)
        block_conect["out"].append(conect_out)

    #どのブロックから自分のブロックに向かうか調べる
    conect_in = [[] for _ in range(len(block_conect["out"]))]
    for i in range(len(block_conect["out"])):
        for j in block_conect["out"][i]:
            if j == "func":
                continue
            conect_in[j].append(i)
    block_conect["in"] = conect_in
    for i in range(len(code)):
        if code[i][0][0] == "func":
            conect_in[i].append("func")
        if i != 0:
            if "func" in block_conect["out"][i - 1]:
                conect_in[i].append("func")

    #out側の繋がっているブロックのお互いが一致しているレジスタのみのリストを作る
    for i in range(len(block_conect["out"])):
        conect_register_out = register_list[i][-1].copy()
        #関数で繋がっている場合はレジスタをリセットさせる
        if "func" in block_conect["out"][i]:
            block_conect["last"].append(["0" for _ in range(len(register_list[0][0]))])
            #0番目のレジスタは常にゼロレジスタ
            block_conect["last"][i][0] = "r0"
            continue
        #最後のブロックならレジスタからメモリに書き込む
        if block_conect["out"][i] == []:
            block_conect["last"].append(["0" for _ in range(len(register_list[0][0]))])
            #0番目のレジスタは常にゼロレジスタ
            block_conect["last"][i][0] = "r0"
            continue
        for j in range(len(block_conect["out"][i])):
            for k in range(len(register_list[i][0])):
                if register_list[i][-1][k] != register_list[block_conect["out"][i][j]][0][k]:
                    conect_register_out[k] = "0"
        block_conect["last"].append(conect_register_out)

    #out側の繋がっているブロックのお互いが一致しているレジスタのみのリストを作る
    for i in range(len(block_conect["in"])):
        conect_register_in = register_list[i][0].copy()
        #関数で繋がっている場合はレジスタをリセットさせる
        if "func" in block_conect["in"][i]:
            block_conect["first"].append(["0" for _ in range(len(register_list[0][0]))])
            #0番目のレジスタは常にゼロレジスタ
            block_conect["first"][i][0] = "r0"
            continue
        #スタートブロックならレジスタを空にする
        if block_conect["in"][i] == []:
            block_conect["first"].append(["0" for _ in range(len(register_list[0][0]))])
            #0番目のレジスタは常にゼロレジスタ
            block_conect["first"][i][0] = "r0"
            continue
        for j in range(len(block_conect["in"][i])):
            for k in range(len(register_list[i][0])):
                if register_list[i][0][k] != register_list[block_conect["in"][i][j]][-1][k]:
                    conect_register_in[k] = "0"
        block_conect["first"].append(conect_register_in)

    #レジスタ配置のリストに追加する
    for i in range(len(register_list)):
        register_list[i].insert(0, block_conect["first"][i])
        register_list[i].append(block_conect["last"][i])

    if debugging:
        for i in range(len(register_list)):
            print(f"ここから、ブロック{i}のレジスタ割り当て")
            print(f"ここには、{block_conect["in"][i]}ブロックから来ます")
            for j in register_list[i]:
                print(j)
            print(f"ここから、{block_conect["out"][i]}ブロックへ向かいます")
            print(f"ここまで、ブロック{i}のレジスタ割り当て")

    return register_list


def convert_mir1_to_msa1(blocks):

    #msa1を書き込むリスト
    program_msa1 = []

    for chunk in range(len(blocks["block"])):

        #チャンク別のプログラム
        program = []

        for block in range(len(blocks["block"][chunk])):

            for instruction in range(len(blocks["block"][chunk][block])):

                #ラベルや関数定義の場合はレジスタにロードするためにレジスタ管理より前に追加する
                if blocks["block"][chunk][block][instruction][0] == "label":
                    program.append(blocks["block"][chunk][block][instruction])
                elif blocks["block"][chunk][block][instruction][0] == "func":
                    program.append(blocks["block"][chunk][block][instruction])

                #命令実行時のレジスタ管理のメモリアクセス
                for i in range(len(blocks["register"][0][0][0])):
                    if blocks["register"][chunk][block][instruction][i] != blocks["register"][chunk][block][instruction + 1][i]:
                        if blocks["register"][chunk][block][instruction][i] != "0":
                            program.append((
                                "0",
                                "7",
                                "0",
                                str(i),
                                str(int(blocks["register"][chunk][block][instruction][i].split("r")[1]) // 16),
                                str(int(blocks["register"][chunk][block][instruction][i].split("r")[1]) % 16)
                            ))
                        program.append((
                            "0",
                            "6",
                            "0",
                            str(i),
                            str(int(blocks["register"][chunk][block][instruction + 1][i].split("r")[1]) // 16),
                            str(int(blocks["register"][chunk][block][instruction + 1][i].split("r")[1]) % 16)
                        ))

                #mir1命令をmsa1命令に変換
                if blocks["block"][chunk][block][instruction][0] == "move":
                    if "r" in blocks["block"][chunk][block][instruction][2]:
                        program.append((
                            "0",
                            "0",
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][1]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                            "0",
                            "0"
                        ))
                    else:
                        program.append((
                            "0",
                            "2",
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][1]),
                            "0",
                            str(int(blocks["block"][chunk][block][instruction][2]) // 16),
                            str(int(blocks["block"][chunk][block][instruction][2]) % 16)
                        ))
                elif blocks["block"][chunk][block][instruction][0] == "add":
                    if "r" in blocks["block"][chunk][block][instruction][3]:
                        program.append((
                            "0",
                            "0",
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][1]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][3]),
                            "0"
                        ))
                    else:
                        program.append((
                            "0",
                            "2",
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][1]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                            str(int(blocks["block"][chunk][block][instruction][3]) // 16),
                            str(int(blocks["block"][chunk][block][instruction][3]) % 16)
                        ))
                elif blocks["block"][chunk][block][instruction][0] == "sub":
                    if "r" in blocks["block"][chunk][block][instruction][3]:
                        program.append((
                            "0",
                            "1",
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][1]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][3]),
                            "0"
                        ))
                    else:
                        program.append((
                            "0",
                            "2",
                            "15",
                            "0",
                            str(int(blocks["block"][chunk][block][instruction][3]) // 16),
                            str(int(blocks["block"][chunk][block][instruction][3]) % 16)
                        ))
                        program.append((
                            "0",
                            "1",
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][1]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                            "15",
                            "0"
                        ))
                if blocks["block"][chunk][block][instruction][0] == "input":
                    program.append((
                        "0",
                        "4",
                        blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][1]),
                        "0",
                        blocks["block"][chunk][block][instruction][2],
                        "0"
                    ))
                elif blocks["block"][chunk][block][instruction][0] == "output":
                    if "r" in blocks["block"][chunk][block][instruction][2]:
                        program.append((
                            "0",
                            "5",
                            "0",
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                            blocks["block"][chunk][block][instruction][1],
                            "0"
                        ))
                    else:
                        program.append((
                            "0",
                            "2",
                            "15",
                            "0",
                            str(int(blocks["block"][chunk][block][instruction][2]) // 16),
                            str(int(blocks["block"][chunk][block][instruction][2]) % 16)
                        ))
                        program.append((
                            "0",
                            "5",
                            "0",
                            "15",
                            blocks["block"][chunk][block][instruction][1],
                            "0"
                        ))
                elif blocks["block"][chunk][block][instruction][0] == "mullo":
                    if "r" in blocks["block"][chunk][block][instruction][3]:
                        program.append((
                            "0",
                            "10",
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][1]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][3]),
                            "0"
                        ))
                    else:
                        program.append((
                            "0",
                            "2",
                            "15",
                            "0",
                            str(int(blocks["block"][chunk][block][instruction][3]) // 16),
                            str(int(blocks["block"][chunk][block][instruction][3]) % 16)
                        ))
                        program.append((
                            "0",
                            "10",
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][1]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                            "15",
                            "0"
                        ))
                elif blocks["block"][chunk][block][instruction][0] == "mulhi":
                    if "r" in blocks["block"][chunk][block][instruction][3]:
                        program.append((
                            "0",
                            "11",
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][1]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][3]),
                            "0"
                        ))
                    else:
                        program.append((
                            "0",
                            "2",
                            "15",
                            "0",
                            str(int(blocks["block"][chunk][block][instruction][3]) // 16),
                            str(int(blocks["block"][chunk][block][instruction][3]) % 16)
                        ))
                        program.append((
                            "0",
                            "11",
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][1]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                            "15",
                            "0"
                        ))
                elif blocks["block"][chunk][block][instruction][0] == "div":
                    if "r" in blocks["block"][chunk][block][instruction][3]:
                        program.append((
                            "0",
                            "12",
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][1]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][3]),
                            "0"
                        ))
                    else:
                        program.append((
                            "0",
                            "2",
                            "15",
                            "0",
                            str(int(blocks["block"][chunk][block][instruction][3]) // 16),
                            str(int(blocks["block"][chunk][block][instruction][3]) % 16)
                        ))
                        program.append((
                            "0",
                            "12",
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][1]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                            "15",
                            "0"
                        ))
                elif blocks["block"][chunk][block][instruction][0] == "mod":
                    if "r" in blocks["block"][chunk][block][instruction][3]:
                        program.append((
                            "0",
                            "13",
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][1]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][3]),
                            "0"
                        ))
                    else:
                        program.append((
                            "0",
                            "2",
                            "15",
                            "0",
                            str(int(blocks["block"][chunk][block][instruction][3]) // 16),
                            str(int(blocks["block"][chunk][block][instruction][3]) % 16)
                        ))
                        program.append((
                            "0",
                            "13",
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][1]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                            "15",
                            "0"
                        ))
                elif blocks["block"][chunk][block][instruction][0] == "rishift":
                        program.append((
                            "0",
                            "9",
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][1]),
                            blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                            blocks["block"][chunk][block][instruction][3],
                            "0"
                        ))

                #ブロック最後のレジスタ管理のメモリアクセス
                if instruction + 1 == len(blocks["block"][chunk][block]):
                    for i in range(len(blocks["register"][0][0][0])):
                        if blocks["register"][chunk][block][instruction + 1][i] != blocks["register"][chunk][block][instruction + 2][i]:
                            program.append((
                                "0",
                                "7",
                                "0",
                                str(i),
                                str(int(blocks["register"][chunk][block][instruction + 1][i].split("r")[1]) // 16),
                                str(int(blocks["register"][chunk][block][instruction + 1][i].split("r")[1]) % 16)
                            ))
                            if blocks["register"][chunk][block][instruction + 2][i] != "0":
                                program.append((
                                    "0",
                                    "6",
                                    "0",
                                    str(i),
                                    str(int(blocks["register"][chunk][block][instruction + 2][i].split("r")[1]) // 16),
                                    str(int(blocks["register"][chunk][block][instruction + 2][i].split("r")[1]) % 16)
                                ))

                if blocks["block"][chunk][block][instruction][0] == "jump":
                    program.append([
                        "0",
                        "3",
                        "0",
                        "0",
                        "0",
                        blocks["block"][chunk][block][instruction][1]
                    ])
                elif blocks["block"][chunk][block][instruction][0] == "if":
                    if blocks["block"][chunk][block][instruction][1] == "eq":
                        if "r" in blocks["block"][chunk][block][instruction][3]:
                            program.append((
                                "0",
                                "1",
                                "0",
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][3]),
                                "0"
                            ))
                            program.append([
                                "0",
                                "3",
                                "2",
                                "0",
                                "0",
                                blocks["block"][chunk][block][instruction][4]
                            ])
                        else:
                            program.append((
                                "0",
                                "2",
                                "15",
                                "0",
                                str(int(blocks["block"][chunk][block][instruction][3]) // 16),
                                str(int(blocks["block"][chunk][block][instruction][3]) % 16)
                            ))
                            program.append((
                                "0",
                                "1",
                                "0",
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                                "15",
                                "0"
                            ))
                            program.append([
                                "0",
                                "3",
                                "2",
                                "0",
                                "0",
                                blocks["block"][chunk][block][instruction][4]
                            ])
                    elif blocks["block"][chunk][block][instruction][1] == "neq":
                        if "r" in blocks["block"][chunk][block][instruction][3]:
                            program.append((
                                "0",
                                "1",
                                "0",
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][3]),
                                "0"
                            ))
                            program.append([
                                "0",
                                "3",
                                "6",
                                "0",
                                "0",
                                blocks["block"][chunk][block][instruction][4]
                            ])
                        else:
                            program.append((
                                "0",
                                "2",
                                "15",
                                "0",
                                str(int(blocks["block"][chunk][block][instruction][3]) // 16),
                                str(int(blocks["block"][chunk][block][instruction][3]) % 16)
                            ))
                            program.append((
                                "0",
                                "1",
                                "0",
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                                "15",
                                "0"
                            ))
                            program.append([
                                "0",
                                "3",
                                "6",
                                "0",
                                "0",
                                blocks["block"][chunk][block][instruction][4]
                            ])
                    elif blocks["block"][chunk][block][instruction][1] == "bi":
                        if "r" in blocks["block"][chunk][block][instruction][3]:
                            program.append((
                                "0",
                                "1",
                                "0",
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][3]),
                                "0"
                            ))
                            program.append([
                                "0",
                                "3",
                                "1",
                                "0",
                                "0",
                                blocks["block"][chunk][block][instruction][4]
                            ])
                        else:
                            program.append((
                                "0",
                                "2",
                                "15",
                                "0",
                                str(int(blocks["block"][chunk][block][instruction][3]) // 16),
                                str(int(blocks["block"][chunk][block][instruction][3]) % 16)
                            ))
                            program.append((
                                "0",
                                "1",
                                "0",
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                                "15",
                                "0"
                            ))
                            program.append([
                                "0",
                                "3",
                                "1",
                                "0",
                                "0",
                                blocks["block"][chunk][block][instruction][4]
                            ])
                    elif blocks["block"][chunk][block][instruction][1] == "nbi":
                        if "r" in blocks["block"][chunk][block][instruction][3]:
                            program.append((
                                "0",
                                "1",
                                "0",
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][3]),
                                "0"
                            ))
                            program.append([
                                "0",
                                "3",
                                "5",
                                "0",
                                "0",
                                blocks["block"][chunk][block][instruction][4]
                            ])
                        else:
                            program.append((
                                "0",
                                "2",
                                "15",
                                "0",
                                str(int(blocks["block"][chunk][block][instruction][3]) // 16),
                                str(int(blocks["block"][chunk][block][instruction][3]) % 16)
                            ))
                            program.append((
                                "0",
                                "1",
                                "0",
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                                "15",
                                "0"
                            ))
                            program.append([
                                "0",
                                "3",
                                "5",
                                "0",
                                "0",
                                blocks["block"][chunk][block][instruction][4]
                            ])
                    elif blocks["block"][chunk][block][instruction][1] == "od":
                        if "r" in blocks["block"][chunk][block][instruction][3]:
                            program.append((
                                "0",
                                "0",
                                "0",
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][3]),
                                "0"
                            ))
                            program.append([
                                "0",
                                "3",
                                "3",
                                "0",
                                "0",
                                blocks["block"][chunk][block][instruction][4]
                            ])
                        else:
                            program.append((
                                "0",
                                "2",
                                "15",
                                "0",
                                str(int(blocks["block"][chunk][block][instruction][3]) // 16),
                                str(int(blocks["block"][chunk][block][instruction][3]) % 16)
                            ))
                            program.append((
                                "0",
                                "0",
                                "0",
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                                "15",
                                "0"
                            ))
                            program.append([
                                "0",
                                "3",
                                "3",
                                "0",
                                "0",
                                blocks["block"][chunk][block][instruction][4]
                            ])
                    elif blocks["block"][chunk][block][instruction][1] == "nod":
                        if "r" in blocks["block"][chunk][block][instruction][3]:
                            program.append((
                                "0",
                                "1",
                                "0",
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][3]),
                                "0"
                            ))
                            program.append([
                                "0",
                                "3",
                                "7",
                                "0",
                                "0",
                                blocks["block"][chunk][block][instruction][4]
                            ])
                        else:
                            program.append((
                                "0",
                                "2",
                                "15",
                                "0",
                                str(int(blocks["block"][chunk][block][instruction][3]) // 16),
                                str(int(blocks["block"][chunk][block][instruction][3]) % 16)
                            ))
                            program.append((
                                "0",
                                "1",
                                "0",
                                blocks["register"][chunk][block][instruction + 1].index(blocks["block"][chunk][block][instruction][2]),
                                "15",
                                "0"
                            ))
                            program.append([
                                "0",
                                "3",
                                "7",
                                "0",
                                "0",
                                blocks["block"][chunk][block][instruction][4]
                            ])
                elif blocks["block"][chunk][block][instruction][0] == "return":
                    program.append((
                        "0",
                        "8",
                        "1",
                        "0",
                        "0",
                        "0"
                    ))
                elif blocks["block"][chunk][block][instruction][0] == "call":
                    program.append([
                        "0",
                        "8",
                        "0",
                        "0",
                        "0",
                        blocks["block"][chunk][block][instruction][1]
                    ])

        #ラベルをアドレスに変換
        #[label or func, number, address]を保存するリスト
        label_address = []
        #既存関数の行もカウントしてアドレスに変換
        kison_code_count = 0
        for i in program_msa1:
            kison_code_count += len(i)
        for i in range(len(program)):
            if program[i][0] == "label":
                label_address.append(("label", program[i][1], i - len(label_address) + kison_code_count))
            elif program[i][0] == "func":
                label_address.append(("func", program[i][1], i - len(label_address) + kison_code_count))

        for i in range(len(program)):
            if program[i][0] == "0":
                if program[i][1] == "3":
                    for type, number, address in label_address:
                        if type == "label" and program[i][5] == number:
                            program[i][4] = str(address // 16)
                            program[i][5] = str(address % 16)
                            break

        codeKARI = program.copy()
        program = []
        for i in codeKARI:
            if i[0] == "label":
                continue
            else:
                program.append(list(i))

        program_msa1.append(program)

    #最後に1つのプログラムにまとめる

    program = []

    for i in program_msa1:
        for j in i:
            program.append(j)

    #関数をアドレスに変換
    #[label or func, number, address]を保存するリスト
    label_address = []
    for i in range(len(program)):
        if program[i][0] == "func":
            label_address.append(("func", program[i][1], i - len(label_address)))

    for i in range(len(program)):
        if program[i][0] == "0":
            if program[i][1] == "8" and program[i][2] == "0":
                for type, number, address in label_address:
                    if type == "func" and program[i][5] == number:
                        program[i][4] = str(address // 16)
                        program[i][5] = str(address % 16)
                        break

    codeKARI = program.copy()
    program = []
    for i in codeKARI:
        if i[0] == "func":
            continue
        else:
            program.append(list(i))

    #0から15を0からFの16進数に変換
    hex_list = {"10": "A", "11": "B", "12": "C", "13": "D", "14": "E", "15": "F"}
    for i in range(len(program)):
        for j in range(len(program[i])):
            if int(program[i][j]) > 9:
                program[i][j] = hex_list[str(program[i][j])]

    return program



if __name__ == "__main__":

    #program.csvとして出力するコード
    code = [
        ["0", "0", "0"],
        ["+X", "+Z"],
        ["16", "4"]
    ]

    #mir1Codeの中身
    source_code = []

    # CSV ファイルを開く
    with open('mir1Code.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        
        # 行を逐次読み取る
        for row in reader:
            source_code.append(row)

    if debugging:
        print("ここから、読み取ったmir1プログラム")
        for i in source_code:
            print(i)
        print("ここまで、読み取ったmir1プログラム")

    #各ブロックのコードやレジスタ割り当てを入れる辞書
    source_code_blocks = {"chunk": [], "block": [], "register": []}

    #mir1をチャンク単位で分割する
    source_code_blocks["chunk"] = chunk_split(source_code)

    #mir1のチャンクをブロック単位で分割する
    for i in source_code_blocks["chunk"]:
        source_code_blocks["block"].append(block_split(i))
    
    if debugging:
        for i in range(len(source_code_blocks["chunk"])):
            print(f"ここから、チャンク{i}のブロック")
            for j in source_code_blocks["block"][i]:
                print(j)
            print(f"ここまで、チャンク{i}のブロック")

    #チャンク別、ブロック別のレジスタ割り当て
    registers_list_list = []

    #チャンク別でレジスタ割り当てを決定する
    for i in range(len(source_code_blocks["chunk"])):

        #複数のアルゴリズムの結果を保存するリスト
        argorithm_results = []

        #レジスタ割り当てアルゴリズム0でレジスタ配置
        registers_list = ["0" for _ in range(15)]
        registers_list[0] = "r0"
        registers_list_history = []
        for j in range(len(source_code_blocks["chunk"][i])):
            registers_list = register_list0(source_code_blocks["chunk"][i], j, registers_list)
            registers_list_history.append(registers_list.copy())
        argorithm_results.append(registers_list_history.copy())

        #レジスタ割り当てアルゴリズム1でレジスタ配置
        registers_list = ["0" for _ in range(15)]
        registers_list[0] = "r0"
        registers_list_history = []
        for j in range(len(source_code_blocks["chunk"][i])):
            registers_list = register_list1(source_code_blocks["chunk"][i], j, registers_list)
            registers_list_history.append(registers_list.copy())
        argorithm_results.append(registers_list_history.copy())

        #最もレジスタ配置変更回数が少なかったものを選ぶ
        change_count = []
        for j in range(len(argorithm_results)):
            change_count.append(register_list_change_count(argorithm_results[j]))
        registers_list = argorithm_results[change_count.index(min(change_count))]

        #レジスタ割り当てを最初まで引き延ばす
        registers_list = register_init(registers_list)

        #ブロック単位に分割しながらレジスタ割り当てをsource_code_blocks["register"]に保存する
        registers_list_list.append([])
        for j in range(len(source_code_blocks["block"][i])):
            registers_list_list[-1].append([])
            for k in range(len(source_code_blocks["block"][i][j])):
                registers_list_list[i][-1].append(registers_list[0])
                del registers_list[0]

        if debugging:
            for j in range(len(registers_list_list[i])):
                print(f"ここから、チャンク{i}、ブロック{j}のレジスタ割り当て")
                for k in registers_list_list[i][j]:
                    print(k)
                print(f"ここまで、チャンク{i}、ブロック{j}のレジスタ割り当て")

    #ブロック単位の繋がりを見てレジスタ割り当てを追加する
    for i in range(len(source_code_blocks["chunk"])):
        source_code_blocks["register"].append(register_add_communication(source_code_blocks["block"][i], registers_list_list[i]))

    #レジスタ管理やラベル、関数管理を行いながらmsa1に変換する
    program = convert_mir1_to_msa1(source_code_blocks)


    for i in program:
        code.append(i)


    # CSV ファイルに保存
    with open('program.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # 行を逐次書き出す
        for row in code:
            writer.writerow(row)

    print("program.csv が保存されました")