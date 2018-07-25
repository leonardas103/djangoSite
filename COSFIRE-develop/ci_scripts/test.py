import unittest

class TestMethods(unittest.TestCase):

    def test_import(self):
        import cosfire

    # Simple test for initialization and running of some of the library's components
    def test_init(self):
        import cosfire as c
        import numpy as np
        from PIL import Image

        # Prototype image
        proto = np.asarray(Image.open('line.png').convert('L'), dtype=np.float64)
        cx, cy = (50,50)

        # Subject image
        subject = 255 - np.asarray(Image.open('01_test.tif').convert('RGB'), dtype=np.float64)[:,:,1]
        subject = subject/255

        # Create COSFIRE operator and fit it with the prototype, then apply it to a subject
        c.COSFIRE(
                c.CircleStrategy(c.DoGFilter, ([1,2,3], 1), rhoList=[0,10,20,40], prototype=proto, center=(cx, cy))
               ).fit().transform(subject)


if __name__ == '__main__':
    unittest.main()
