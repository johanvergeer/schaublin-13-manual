from pathlib import Path
from google.cloud import vision
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


def get_outfile_path(page: int) -> Path:
    return Path(
        f"schaublin_13_first_gen/originals/fr/google_vision_results/{page}.json"
    )


def detect_text(page, path):
    """Detects text in the file."""

    if get_outfile_path(page).exists():
        logger.info(f"Page {page} already processed! SKIPPING!")
        return

    client = vision.ImageAnnotatorClient()

    with path.open("rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    result = {
        "locale": texts[0].locale,
        "text": texts[0].description,
        "lines": [
            {
                "description": line.description,
                "confidence": line.confidence,
                "bounding_poly": [
                    {"x": vertex.x, "y": vertex.y}
                    for vertex in line.bounding_poly.vertices
                ],
            }
            for line in texts[1:]
        ],
    }

    with get_outfile_path(page).open("w+") as outfile:
        json.dump(result, outfile)

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )


pages = [57]

for page in pages:
    logger.info(f"Reading page {page}")
    path = Path(
        f"schaublin_13_first_gen/originals/fr/png/Schaublin 13 (modèle 1956-1969) Manuel utilisation-{page:02}.png"
    )

    if not path.exists():
        logger.warning(f"path for page {page} not found!!!!")
        continue

    try:
        detect_text(page, path)
    except:
        logger.exception(f"an error occurred while reading page {page}")
