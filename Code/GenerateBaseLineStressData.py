import Stress

if __name__ == "__main__":
    print("Generating data for overclocking...")
    stress = Stress.Stress()
    stress.Test(baseline=True)
    stress.saveWeight()
    print()