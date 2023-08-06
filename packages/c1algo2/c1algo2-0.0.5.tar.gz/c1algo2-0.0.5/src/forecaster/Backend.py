import sys
import Predictor

# !RP/!JC - Let's load and return a pickle? 
def dummyData() -> dict:
    return {"Dummy": "Data"}

def main() -> dict:
    try:
        if sys.argv[1] == "dummy":
            return dummyData()
    except IndexError:
        pass
    return Predictor.main()

if __name__ == "__main__":
    main()