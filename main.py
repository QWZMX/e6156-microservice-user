from fastapi import FastAPI, Response

# I like to launch directly and not use the standard FastAPI startup
import uvicorn


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8012)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
