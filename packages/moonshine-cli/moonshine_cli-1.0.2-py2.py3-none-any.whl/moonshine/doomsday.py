import os
import argparse

os.system("cls")
print(
    """
                  __                       __         
              ___/ /__  ___  __ _  ___ ___/ /__ ___ __
             / _  / _ \/ _ \/  ' \(_-</ _  / _ `/ // /
             \_,_/\___/\___/_/_/_/___/\_,_/\_,_/\_, / 
                             M O O N S H I N E /___/  
                                              v0.0.1


       """
)


def xocli():

    parser = argparse.ArgumentParser(
        description="Just an example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-a", "--archive", action="store_true", help="add to archive mode"
    )
    parser.add_argument("-e", "--employee", help="Display Employee Information")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="increase verbosity"
    )
    parser.add_argument("-B", "--block-size", help="checksum blocksize")
    parser.add_argument(
        "--ignore-existing", action="store_true", help="skip files that exist"
    )
    parser.add_argument("--exclude", help="files to exclude")
    args = parser.parse_args()
    config = vars(args)
    print(config)


if __name__ == "__main__":
    xocli()
