from pipeline_runner import run

def upload_trigger(files):
    return run(files)

if __name__ == "__main__":
    print(upload_trigger(["A1","A2"]))
