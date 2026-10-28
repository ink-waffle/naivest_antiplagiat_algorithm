from pathlib import Path
import argparse
import io
import re


# Интерпретатор Brainfuck: 8-битные ячейки, лента растёт вправо, EOF читается как 0
def run(program, data):
    # Повторы + - < > сжимаем в одну команду, для скобок заранее находим пару
    code, stack = [], []
    for op in re.findall(r'\++|-+|>+|<+|[\[\].,]', program):
        if op[0] in '+-':
            code.append(('+', len(op) if op[0] == '+' else -len(op)))
        elif op[0] in '<>':
            code.append(('>', len(op) if op[0] == '>' else -len(op)))
        elif op == '[':
            stack.append(len(code))
            code.append(['[', 0])
        elif op == ']':
            start = stack.pop()
            code[start][1] = len(code)
            code.append((']', start))
        else:
            code.append((op, 0))

    tape, ptr, pos, out = [0] * 100000, 0, 0, bytearray()
    pc = 0
    while pc < len(code):
        op, arg = code[pc]
        if op == '+':
            tape[ptr] = (tape[ptr] + arg) % 256
        elif op == '>':
            ptr += arg
            if ptr >= len(tape):
                tape.extend([0] * len(tape))
        elif op == '[':
            if not tape[ptr]:
                pc = arg
        elif op == ']':
            if tape[ptr]:
                pc = arg
        elif op == '.':
            out.append(tape[ptr])
        elif op == ',':
            tape[ptr] = data[pos] if pos < len(data) else 0
            pos += 1
        pc += 1
    return out.decode()


# Основной блок: пары файлов подаются на вход compare.bf через байт 0xFF, его вывод записывается в файл
def main(input_dir, output_dir):
    data = b''
    for files in io.open(input_dir, 'r', encoding='utf-8'):
        if files.strip() != '':
            file1, file2 = files.split()
            data += Path(file1).read_bytes() + b'\xff' + Path(file2).read_bytes() + b'\xff'

    program = Path(__file__).with_name('compare.bf').read_text(encoding='utf-8')
    with open(output_dir, 'w') as out:
        out.write(run(program, data))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Files to process')
    parser.add_argument('indir', type=str, help='Input dir for files')
    parser.add_argument('outdir', type=str, help='Output dir for score file')
    args = parser.parse_args()

    main(args.indir, args.outdir)
