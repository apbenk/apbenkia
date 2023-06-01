from flask import Flask, render_template, request
import azure.ai.vision as sdk

app = Flask(__name__)

# Replace the placeholders with your actual vision endpoint and key
VISION_ENDPOINT = "https://apbenk-computervision.cognitiveservices.azure.com/"
VISION_KEY = "33258c4ef59244949ae0eb9fb8ccad54"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form['url']

    service_options = sdk.VisionServiceOptions(VISION_ENDPOINT, VISION_KEY)
    vision_source = sdk.VisionSource(url=url)

    analysis_options = sdk.ImageAnalysisOptions()
    analysis_options.features = (
        sdk.ImageAnalysisFeature.CAPTION |
        sdk.ImageAnalysisFeature.TEXT
    )
    analysis_options.language = "en"
    analysis_options.gender_neutral_caption = True

    image_analyzer = sdk.ImageAnalyzer(service_options, vision_source, analysis_options)
    result = image_analyzer.analyze()

    if result.reason == sdk.ImageAnalysisResultReason.ANALYZED:
        captions = []
        texts = []
        if result.caption is not None:
            captions.append(result.caption.content)

        if result.text is not None:
            for line in result.text.lines:
                words = []
                for word in line.words:
                    words.append(word.content)
                texts.append(" ".join(words))

        return render_template('result.html', captions=captions, texts=texts)
    else:
        error_details = sdk.ImageAnalysisErrorDetails.from_result(result)
        error_message = "Analysis failed.\nError reason: {}\nError code: {}\nError message: {}".format(
            error_details.reason, error_details.error_code, error_details.message
        )
        return render_template('error.html', error_message=error_message)

if __name__ == '__main__':
    app.run()
