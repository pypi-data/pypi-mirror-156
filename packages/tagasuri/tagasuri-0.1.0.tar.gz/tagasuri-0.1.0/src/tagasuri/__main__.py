import argparse
import tagasuri
from tagasuri.analysis import Analysis


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--engine-file', type=str, required=True,
        help='Input engine file. Required=True.')
    parser.add_argument(
        '--input-file', type=str, required=True,
        help='Input pgn file. Required=True.')
    parser.add_argument(
        '--move-time', type=float, required=False,
        default = 1.0,
        help='Input movetime in seconds. Required=False, default=1.0')
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'{tagasuri.__version__}')

    args = parser.parse_args()

    a = Analysis(args.engine_file, args.input_file, args.move_time)
    a.run()
    totalpos = a.totalpos
    correct = a.correct
    print(f'total: {totalpos}, correct: {correct}, correct%: {100*correct/totalpos:0.2f}')


if __name__ == '__main__':
    main()
