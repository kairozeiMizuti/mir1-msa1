#このプログラムはChatGPTが書いたコードです

"""
ROM Writer for Minecraft Java Edition 1.20.4
Part 1

機能
・設定
・信号強度テーブル生成
・NBT生成
"""

import math
import csv
from pathlib import Path

# ==========================================================
# 設定
# ==========================================================

ITEM_ID = "minecraft:redstone"
OUTPUT_FILE = "romcode.mcfunction"

STACK_SIZE = 64
BARREL_SLOTS = 27
BARREL_CAPACITY = STACK_SIZE * BARREL_SLOTS

VALID_DIRECTIONS = {
    "+X": (1, 0),
    "-X": (-1, 0),
    "+Z": (0, 1),
    "-Z": (0, -1),
}


# ==========================================================
# エラー
# ==========================================================

class ROMWriterError(Exception):
    pass


# ==========================================================
# コンパレータ
# ==========================================================

class ComparatorCalculator:

    @staticmethod
    def signal_strength(item_count: int) -> int:
        """
        アイテム総数からコンパレータ信号強度を返す

        ※64スタックアイテム専用
        """

        if item_count <= 0:
            return 0

        fullness = item_count / BARREL_CAPACITY

        return math.floor(fullness * 14) + 1


# ==========================================================
# 信号強度テーブル
# ==========================================================

class SignalTable:

    def __init__(self):

        self.table = {}

        self.generate()

    def generate(self):

        for signal in range(16):

            self.table[signal] = self.find_minimum_items(signal)

    def find_minimum_items(self, signal):

        if signal == 0:
            return 0

        for count in range(BARREL_CAPACITY + 1):

            if ComparatorCalculator.signal_strength(count) == signal:
                return count

        raise ROMWriterError(
            f"信号強度 {signal} のアイテム数を見つけられません。"
        )

    def get(self, signal):

        return self.table[signal]


# ==========================================================
# 樽NBT生成
# ==========================================================

class BarrelNBT:

    def __init__(self, table: SignalTable):

        self.table = table

    def create_items(self, signal):

        total = self.table.get(signal)

        if total == 0:
            return []

        items = []

        slot = 0

        while total > 0:

            amount = min(total, STACK_SIZE)

            items.append({
                "Slot": slot,
                "Count": amount
            })

            slot += 1
            total -= amount

        return items

    def to_nbt(self, signal):

        items = self.create_items(signal)

        if len(items) == 0:
            return "{}"

        nbt = []

        for item in items:

            nbt.append(
                (
                    "{"
                    f'Slot:{item["Slot"]}b,'
                    f'id:"{ITEM_ID}",'
                    f'Count:{item["Count"]}b'
                    "}"
                )
            )

        return "{Items:[" + ",".join(nbt) + "]}"


class CSVReader:

    def __init__(self, filename):

        self.filename = Path(filename)

        self.start = None
        self.main_direction = None
        self.turn_direction = None

        self.fold_width = None
        self.fold_spacing = None
        self.program = []

    def load(self):

        if not self.filename.exists():
            raise ROMWriterError("CSVファイルがありません。")

        with self.filename.open(
            encoding="utf-8-sig",
            newline=""
        ) as f:

            rows = []

            for row in csv.reader(f):

                # 空行を無視
                if len(row) == 0:
                    continue

                # 1列目が空なら無視
                if row[0].strip() == "":
                    continue

                # コメント行を無視
                if row[0].strip().startswith("#"):
                    continue

                rows.append(row)

        # 現在のCSV仕様では最低4行必要
        if len(rows) < 4:
            raise ROMWriterError(
                "CSVは4行以上必要です。"
            )

        # 1行目：開始座標
        self.read_start(rows[0])

        # 2行目：方向
        self.read_direction(rows[1])

        # 3行目：折り返し設定
        self.read_fold(rows[2])

        # 4行目以降：プログラム
        self.read_program(rows[3:])

    def read_start(self, row):

        if len(row) != 3:

            raise ROMWriterError(
                "開始座標は3つ指定してください。"
            )

        try:

            x = int(row[0])
            y = int(row[1])
            z = int(row[2])

        except:

            raise ROMWriterError(
                "開始座標は整数で指定してください。"
            )

        self.start = (x, y, z)

    def read_direction(self, row):

        if len(row) != 2:
            raise ROMWriterError(
                "方向は2つ指定してください。"
            )

        main = row[0].strip().upper()
        turn = row[1].strip().upper()

        if main not in VALID_DIRECTIONS:
            raise ROMWriterError(
                "メイン方向は +X -X +Z -Z のみです。"
            )

        if turn not in VALID_DIRECTIONS:
            raise ROMWriterError(
                "折り返し方向は +X -X +Z -Z のみです。"
            )

        self.main_direction = main
        self.turn_direction = turn

    def read_fold(self, row):

        if len(row) != 2:

            raise ROMWriterError(
                "折り返し設定は 幅,間隔 です。"
            )

        self.fold_width = int(row[0])

        self.fold_spacing = int(row[1])

        if self.fold_width <= 0:
            raise ROMWriterError(
                "折り返し幅は1以上"
            )

        if self.fold_spacing <= 0:
            raise ROMWriterError(
                "間隔は1以上"
            )

    def read_program(self, rows):

        width = len(rows[0])

        for y, row in enumerate(rows):

            if len(row) != width:

                raise ROMWriterError(
                    f"{y+4}行目の列数が一致しません。"
                )

            line = []

            for x, value in enumerate(row):

                value = value.strip().upper()

                if len(value) != 1:

                    raise ROMWriterError(
                        f"{y+4}行 {x+1}列"
                    )

                if value not in "0123456789ABCDEF":

                    raise ROMWriterError(
                        f"{y+4}行 {x+1}列 : {value}"
                    )

                line.append(
                    int(value,16)
                )

            self.program.append(line)


class CoordinateCalculator:

    def __init__(
        self,
        start,
        main_direction,
        turn_direction,
        fold_width,
        fold_spacing
    ):

        self.x,self.y,self.z = start

        self.main_dx, self.main_dz = VALID_DIRECTIONS[
            main_direction
        ]

        self.turn_dx, self.turn_dz = VALID_DIRECTIONS[
            turn_direction
        ]

        self.fold_width = fold_width
        self.fold_spacing = fold_spacing

    def get(self, column, row):

        page = column // self.fold_width
        offset = column % self.fold_width

        x = (
            self.x
            + offset * 2 * self.main_dx
            + page * self.fold_spacing * self.turn_dx
        )

        y = self.y - row * 2

        z = (
            self.z
            + offset * 2 * self.main_dz
            + page * self.fold_spacing * self.turn_dz
        )

        return x,y,z


# ==========================================================
# mcfunction生成
# ==========================================================

class MCFunctionWriter:

    def __init__(self, reader, table):

        self.reader = reader
        self.barrel = BarrelNBT(table)

        self.coord = CoordinateCalculator(
            reader.start,
            reader.main_direction,
            reader.turn_direction,
            reader.fold_width,
            reader.fold_spacing
        )

    def write(self, filename):

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:

            for column, line in enumerate(self.reader.program):

                for row, signal in enumerate(line):

                    x, y, z = self.coord.get(
                        column,
                        row
                    )

                    nbt = self.barrel.to_nbt(signal)

                    # 一度空気にする
                    f.write(
                        f"setblock {x} {y} {z} minecraft:air\n"
                    )

                    # 樽を設置
                    f.write(
                        f'setblock {x} {y} {z} minecraft:barrel{nbt}\n'
                    )

        print()

        print("生成完了")

        print(filename)


# ==========================================================
# テスト
# ==========================================================

if __name__ == "__main__":

    try:

        reader = CSVReader(
            "program.csv"
        )

        reader.load()

        table = SignalTable()

        writer = MCFunctionWriter(
            reader,
            table
        )

        writer.write(
            OUTPUT_FILE
        )

    except ROMWriterError as e:

        print()

        print("エラー")

        print(e)

    except Exception as e:

        print()

        print("予期しないエラー")

        print(e)