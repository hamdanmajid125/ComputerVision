import cv2
import numpy as np
from typing import Tuple


class PencilSketch:
    """Apply pencil sketch effect to an image"""
    def __init__(
        self,
        blur_simga: int = 5,
        ksize: Tuple[int, int] = (0, 0),
        sharpen_value: int = None,
        kernel: np.ndarray = None,
    ) -> None:
        """
        Args:
            blur_simga: (int) - sigma ratio to apply for cv2.GaussianBlur
            ksize: (float) - ratio to apply for cv2.GaussianBlur
            sharpen_value: (int) - sharpen value to apply in predefined kernel array
            kernel: (np.ndarray) - custom kernel to apply in sharpen function
        """
        self.blur_simga = blur_simga
        self.ksize = ksize
        self.sharpen_value = sharpen_value
        self.kernel = np.array(
            [[0, -1, 0], [-1, sharpen_value, -1], [0, -1, 0]]
        ) if kernel is None and sharpen_value is not None else kernel

    def dodge(self, front: np.ndarray, back: np.ndarray) -> np.ndarray:
        """The formula comes from https://en.wikipedia.org/wiki/Blend_modes
        Args:
            front: (np.ndarray) - front image to be applied to dodge algorithm
            back: (np.ndarray) - back image to be applied to dodge algorithm

        Returns:
            image: (np.ndarray) - dodged image
        """
        result = back * 255.0 / (255.0 - front)
        result[result > 255] = 255
        result[back == 255] = 255
        return result.astype('uint8')

    def sharpen(self, image: np.ndarray) -> np.ndarray:
        """Sharpen image by defined kernel size
        Args:
            image: (np.ndarray) - image to be sharpened

        Returns:
            image: (np.ndarray) - sharpened image
        """
        if self.sharpen_value is not None and isinstance(self.sharpen_value, int):
            inverted = 255 - image
            return 255 - cv2.filter2D(src=inverted, ddepth=-1, kernel=self.kernel)

        return image

    def __call__(self, frame: np.ndarray) -> np.ndarray:
        """Main function to do pencil sketch
        Args:
            frame: (np.ndarray) - frame to execute pencil sketch on

        Returns:
            frame: (np.ndarray) - processed frame that is pencil sketch type
        """
        grayscale = np.array(
            np.dot(frame[..., :3], [0.299, 0.587, 0.114]), dtype=np.uint8
        )
        grayscale = np.stack((grayscale,) * 3, axis=-1)  # Convert grayscale to 3-channel

        inverted_img = 255 - grayscale

        blur_img = cv2.GaussianBlur(
            inverted_img, ksize=self.ksize, sigmaX=self.blur_simga
        )

        final_img = self.dodge(blur_img, grayscale)

        sharpened_image = self.sharpen(final_img)

        return sharpened_image


# Use the PencilSketch class to process an image
if __name__ == "__main__":
    # Load the image
    image_path = "hamdan.jpg"
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Image at {image_path} could not be loaded.")

    # Create the PencilSketch instance
    pencil_sketch = PencilSketch(blur_simga=5, ksize=(21, 21), sharpen_value=10)

    # Apply the pencil sketch effect
    sketch_image = pencil_sketch(image)

    # Display the image
    cv2.imshow("Original Image", image)
    cv2.imshow("Pencil Sketch", sketch_image)

    # Save the sketch image
    output_path = "pencil_sketch.jpg"
    cv2.imwrite(output_path, sketch_image)

    # Wait for a key press and close the windows
    cv2.waitKey(0)
    cv2.destroyAllWindows()
