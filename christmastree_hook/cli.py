import sys
from . import check_import_length_order


def main() -> int:
    # Delegate directly to the hook script's main
    return check_import_length_order.main(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
