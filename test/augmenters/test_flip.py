from __future__ import print_function, division, absolute_import

import time
import sys
# unittest only added in 3.4 self.subTest()
if sys.version_info[0] < 3 or sys.version_info[1] < 4:
    import unittest2 as unittest
else:
    import unittest
# unittest.mock is not available in 2.7 (though unittest2 might contain it?)
try:
    import unittest.mock as mock
except ImportError:
    import mock
import warnings

import matplotlib
matplotlib.use('Agg')  # fix execution of tests involving matplotlib on travis
import numpy as np
import six.moves as sm

import imgaug as ia
from imgaug import augmenters as iaa
from imgaug import parameters as iap
from imgaug import dtypes as iadt
from imgaug.testutils import keypoints_equal, reseed
from imgaug.augmentables.heatmaps import HeatmapsOnImage
from imgaug.augmentables.segmaps import SegmentationMapsOnImage
import imgaug.augmenters.flip as fliplib


def main():
    time_start = time.time()

    test_HorizontalFlip()
    test_VerticalFlip()
    test_Fliplr()
    test_Flipud()

    time_end = time.time()
    print("<%s> Finished without errors in %.4fs." % (__file__, time_end - time_start,))


def test_HorizontalFlip():
    aug = iaa.HorizontalFlip(0.5)
    assert isinstance(aug, iaa.Fliplr)
    assert np.allclose(aug.p.p.value, 0.5)


def test_VerticalFlip():
    aug = iaa.VerticalFlip(0.5)
    assert isinstance(aug, iaa.Flipud)
    assert np.allclose(aug.p.p.value, 0.5)


def test_Fliplr():
    reseed()

    base_img = np.array([[0, 0, 1],
                         [0, 0, 1],
                         [0, 1, 1]], dtype=np.uint8)
    base_img = base_img[:, :, np.newaxis]

    base_img_flipped = np.array([[1, 0, 0],
                                 [1, 0, 0],
                                 [1, 1, 0]], dtype=np.uint8)
    base_img_flipped = base_img_flipped[:, :, np.newaxis]

    images = np.array([base_img])
    images_flipped = np.array([base_img_flipped])

    keypoints = [ia.KeypointsOnImage([ia.Keypoint(x=0, y=0),
                                      ia.Keypoint(x=1, y=1),
                                      ia.Keypoint(x=2, y=2)],
                                     shape=base_img.shape)]
    keypoints_flipped = [ia.KeypointsOnImage([ia.Keypoint(x=3-0, y=0),
                                              ia.Keypoint(x=3-1, y=1),
                                              ia.Keypoint(x=3-2, y=2)],
                                             shape=base_img.shape)]

    polygons = [ia.PolygonsOnImage(
        [ia.Polygon([(0, 0), (2, 0), (2, 2)])],
        shape=base_img.shape)]
    polygons_flipped = [ia.PolygonsOnImage(
        [ia.Polygon([(3-0, 0), (3-2, 0), (3-2, 2)])],
        shape=base_img.shape)]

    # 0% chance of flip
    aug = iaa.Fliplr(0)
    aug_det = aug.to_deterministic()

    for _ in sm.xrange(10):
        observed = aug.augment_images(images)
        expected = images
        assert np.array_equal(observed, expected)

        observed = aug_det.augment_images(images)
        expected = images
        assert np.array_equal(observed, expected)

        observed = aug.augment_keypoints(keypoints)
        expected = keypoints
        assert keypoints_equal(observed, expected)

        observed = aug_det.augment_keypoints(keypoints)
        expected = keypoints
        assert keypoints_equal(observed, expected)

        for aug_ in [aug, aug_det]:
            observed = aug_.augment_polygons(polygons)
            assert len(observed) == 1
            assert len(observed[0].polygons) == 1
            assert observed[0].shape == polygons[0].shape
            assert observed[0].polygons[0].exterior_almost_equals(
                polygons[0].polygons[0])
            assert observed[0].polygons[0].is_valid

    # 0% chance of flip, heatmaps
    aug = iaa.Fliplr(0)
    heatmaps = HeatmapsOnImage(
        np.float32([
            [0, 0.5, 0.75],
            [0, 0.5, 0.75],
            [0.75, 0.75, 0.75],
        ]),
        shape=(3, 3, 3)
    )
    observed = aug.augment_heatmaps([heatmaps])[0]
    expected = heatmaps.get_arr()
    assert observed.shape == heatmaps.shape
    assert heatmaps.min_value - 1e-6 < observed.min_value < heatmaps.min_value + 1e-6
    assert heatmaps.max_value - 1e-6 < observed.max_value < heatmaps.max_value + 1e-6
    assert np.array_equal(observed.get_arr(), expected)

    # 0% chance of flip, segmaps
    aug = iaa.Fliplr(0)
    segmaps = SegmentationMapsOnImage(
        np.int32([
            [0, 1, 2],
            [0, 1, 2],
            [2, 2, 2],
        ]),
        shape=(3, 3, 3)
    )
    observed = aug.augment_segmentation_maps([segmaps])[0]
    expected = segmaps.get_arr()
    assert observed.shape == segmaps.shape
    assert np.array_equal(observed.get_arr(), expected)

    # 100% chance of flip
    aug = iaa.Fliplr(1.0)
    aug_det = aug.to_deterministic()

    for _ in sm.xrange(10):
        observed = aug.augment_images(images)
        expected = images_flipped
        assert np.array_equal(observed, expected)

        observed = aug_det.augment_images(images)
        expected = images_flipped
        assert np.array_equal(observed, expected)

        observed = aug.augment_keypoints(keypoints)
        expected = keypoints_flipped
        assert keypoints_equal(observed, expected)

        observed = aug_det.augment_keypoints(keypoints)
        expected = keypoints_flipped
        assert keypoints_equal(observed, expected)

        for aug_ in [aug, aug_det]:
            observed = aug_.augment_polygons(polygons)
            assert len(observed) == 1
            assert len(observed[0].polygons) == 1
            assert observed[0].shape == polygons[0].shape
            assert observed[0].polygons[0].exterior_almost_equals(
                polygons_flipped[0].polygons[0])
            assert observed[0].polygons[0].is_valid

    # 100% chance of flip, heatmaps
    aug = iaa.Fliplr(1.0)
    heatmaps = HeatmapsOnImage(
        np.float32([
            [0, 0.5, 0.75],
            [0, 0.5, 0.75],
            [0.75, 0.75, 0.75],
        ]),
        shape=(3, 3, 3)
    )
    observed = aug.augment_heatmaps([heatmaps])[0]
    expected = np.fliplr(heatmaps.get_arr())
    assert observed.shape == heatmaps.shape
    assert heatmaps.min_value - 1e-6 < observed.min_value < heatmaps.min_value + 1e-6
    assert heatmaps.max_value - 1e-6 < observed.max_value < heatmaps.max_value + 1e-6
    assert np.array_equal(observed.get_arr(), expected)

    # 100% chance of flip, segmaps
    aug = iaa.Fliplr(1.0)
    segmaps = SegmentationMapsOnImage(
        np.int32([
            [0, 1, 2],
            [0, 1, 2],
            [2, 2, 2],
        ]),
        shape=(3, 3, 3)
    )
    observed = aug.augment_segmentation_maps([segmaps])[0]
    expected = np.fliplr(segmaps.get_arr())
    assert observed.shape == segmaps.shape
    assert np.array_equal(observed.get_arr(), expected)

    # 50% chance of flip
    aug = iaa.Fliplr(0.5)
    aug_det = aug.to_deterministic()

    nb_iterations = 1000
    nb_images_flipped = 0
    nb_images_flipped_det = 0
    nb_keypoints_flipped = 0
    nb_keypoints_flipped_det = 0
    nb_polygons_flipped = 0
    nb_polygons_flipped_det = 0
    for _ in sm.xrange(nb_iterations):
        observed = aug.augment_images(images)
        if np.array_equal(observed, images_flipped):
            nb_images_flipped += 1

        observed = aug_det.augment_images(images)
        if np.array_equal(observed, images_flipped):
            nb_images_flipped_det += 1

        observed = aug.augment_keypoints(keypoints)
        if keypoints_equal(observed, keypoints_flipped):
            nb_keypoints_flipped += 1

        observed = aug_det.augment_keypoints(keypoints)
        if keypoints_equal(observed, keypoints_flipped):
            nb_keypoints_flipped_det += 1

        observed = aug.augment_polygons(polygons)
        if observed[0].polygons[0].exterior_almost_equals(
                polygons_flipped[0].polygons[0]):
            nb_polygons_flipped += 1

        observed = aug_det.augment_polygons(polygons)
        if observed[0].polygons[0].exterior_almost_equals(
                polygons_flipped[0].polygons[0]):
            nb_polygons_flipped_det += 1

    assert int(nb_iterations * 0.3) <= nb_images_flipped <= int(nb_iterations * 0.7)
    assert int(nb_iterations * 0.3) <= nb_keypoints_flipped <= int(nb_iterations * 0.7)
    assert int(nb_iterations * 0.3) <= nb_polygons_flipped <= int(nb_iterations * 0.7)
    assert nb_images_flipped_det in [0, nb_iterations]
    assert nb_keypoints_flipped_det in [0, nb_iterations]
    assert nb_polygons_flipped_det in [0, nb_iterations]

    # 50% chance of flipped, multiple images, list as input
    images_multi = [base_img, base_img]
    aug = iaa.Fliplr(0.5)
    aug_det = aug.to_deterministic()
    nb_iterations = 1000
    nb_flipped_by_pos = [0] * len(images_multi)
    nb_flipped_by_pos_det = [0] * len(images_multi)
    for _ in sm.xrange(nb_iterations):
        observed = aug.augment_images(images_multi)
        for i in sm.xrange(len(images_multi)):
            if np.array_equal(observed[i], base_img_flipped):
                nb_flipped_by_pos[i] += 1

        observed = aug_det.augment_images(images_multi)
        for i in sm.xrange(len(images_multi)):
            if np.array_equal(observed[i], base_img_flipped):
                nb_flipped_by_pos_det[i] += 1

    for val in nb_flipped_by_pos:
        assert int(nb_iterations * 0.3) <= val <= int(nb_iterations * 0.7)

    for val in nb_flipped_by_pos_det:
        assert val in [0, nb_iterations]

    # test StochasticParameter as p
    aug = iaa.Fliplr(p=iap.Choice([0, 1], p=[0.7, 0.3]))
    seen = [0, 0]
    for _ in sm.xrange(1000):
        observed = aug.augment_image(base_img)
        if np.array_equal(observed, base_img):
            seen[0] += 1
        elif np.array_equal(observed, base_img_flipped):
            seen[1] += 1
        else:
            assert False
    assert 700 - 75 < seen[0] < 700 + 75
    assert 300 - 75 < seen[1] < 300 + 75

    # test exceptions for wrong parameter types
    got_exception = False
    try:
        _ = iaa.Fliplr(p="test")
    except Exception:
        got_exception = True
    assert got_exception

    # test get_parameters()
    aug = iaa.Fliplr(p=0.5)
    params = aug.get_parameters()
    assert isinstance(params[0], iap.Binomial)
    assert isinstance(params[0].p, iap.Deterministic)
    assert 0.5 - 1e-4 < params[0].p.value < 0.5 + 1e-4

    ###################
    # test other dtypes
    ###################
    aug = iaa.Fliplr(1.0)

    image = np.zeros((3, 3), dtype=bool)
    image[0, 0] = True
    expected = np.zeros((3, 3), dtype=bool)
    expected[0, 2] = True
    image_aug = aug.augment_image(image)
    assert image_aug.dtype.type == image.dtype.type
    assert np.all(image_aug == expected)

    for dtype in [np.uint8, np.uint16, np.uint32, np.uint64, np.int8, np.int32, np.int64]:
        min_value, center_value, max_value = iadt.get_value_range_of_dtype(dtype)
        value = max_value
        image = np.zeros((3, 3), dtype=dtype)
        image[0, 0] = value
        expected = np.zeros((3, 3), dtype=dtype)
        expected[0, 2] = value
        image_aug = aug.augment_image(image)
        assert image_aug.dtype.type == dtype
        assert np.array_equal(image_aug, expected)

    for dtype, value in zip([np.float16, np.float32, np.float64, np.float128], [5000, 1000**2, 1000**3, 1000**4]):
        atol = 1e-9 * max_value if dtype != np.float16 else 1e-3 * max_value
        image = np.zeros((3, 3), dtype=dtype)
        image[0, 0] = value
        expected = np.zeros((3, 3), dtype=dtype)
        expected[0, 2] = value
        image_aug = aug.augment_image(image)
        assert image_aug.dtype.type == dtype
        assert np.allclose(image_aug, expected, atol=atol)


class Test_fliplr(unittest.TestCase):
    def setUp(self):
        reseed()

    @mock.patch("imgaug.augmenters.flip._fliplr_sliced")
    @mock.patch("imgaug.augmenters.flip._fliplr_cv2")
    def test__fliplr_cv2_called_mocked(self, mock_cv2, mock_sliced):
        for dtype in ["uint8", "uint16", "int8", "int16"]:
            mock_cv2.reset_mock()
            mock_sliced.reset_mock()
            arr = np.zeros((1, 1), dtype=dtype)

            _ = fliplib.fliplr(arr)

            mock_cv2.assert_called_once_with(arr)
            assert mock_sliced.call_count == 0

    @mock.patch("imgaug.augmenters.flip._fliplr_sliced")
    @mock.patch("imgaug.augmenters.flip._fliplr_cv2")
    def test__fliplr_sliced_called_mocked(self, mock_cv2, mock_sliced):
        for dtype in ["bool", "uint32", "uint64", "int32", "int64",
                      "float16", "float32", "float64", "float128"]:
            mock_cv2.reset_mock()
            mock_sliced.reset_mock()
            arr = np.zeros((1, 1), dtype=dtype)

            _ = fliplib.fliplr(arr)

            assert mock_cv2.call_count == 0
            mock_sliced.assert_called_once_with(arr)

    def test__fliplr_cv2_2d(self):
        self._test__fliplr_subfunc_n_channels(fliplib._fliplr_cv2, None)

    def test__fliplr_cv2_3d_single_channel(self):
        self._test__fliplr_subfunc_n_channels(fliplib._fliplr_cv2, 1)

    def test__fliplr_cv2_3d_three_channels(self):
        self._test__fliplr_subfunc_n_channels(fliplib._fliplr_cv2, 3)

    def test__fliplr_cv2_3d_four_channels(self):
        self._test__fliplr_subfunc_n_channels(fliplib._fliplr_cv2, 4)

    def test__fliplr_sliced_2d(self):
        self._test__fliplr_subfunc_n_channels(fliplib._fliplr_sliced, None)

    def test__fliplr_sliced_3d_single_channel(self):
        self._test__fliplr_subfunc_n_channels(fliplib._fliplr_sliced, 1)

    def test__fliplr_sliced_3d_three_channels(self):
        self._test__fliplr_subfunc_n_channels(fliplib._fliplr_sliced, 3)

    def test__fliplr_sliced_3d_four_channels(self):
        self._test__fliplr_subfunc_n_channels(fliplib._fliplr_sliced, 4)

    @classmethod
    def _test__fliplr_subfunc_n_channels(cls, func, nb_channels):
        arr = np.uint8([
            [0, 1, 2, 3],
            [4, 5, 6, 7],
            [10, 11, 12, 13]
        ])
        if nb_channels is not None:
            arr = np.tile(arr[..., np.newaxis], (1, 1, nb_channels))
            for c in sm.xrange(nb_channels):
                arr[..., c] += c

        arr_flipped = func(arr)

        expected = np.uint8([
            [3, 2, 1, 0],
            [7, 6, 5, 4],
            [13, 12, 11, 10]
        ])
        if nb_channels is not None:
            expected = np.tile(expected[..., np.newaxis], (1, 1, nb_channels))
            for c in sm.xrange(nb_channels):
                expected[..., c] += c
        assert arr_flipped.dtype.name == "uint8"
        assert arr_flipped.shape == arr.shape
        assert np.array_equal(arr_flipped, expected)

    def test_zero_width_arr_cv2(self):
        arr = np.zeros((4, 0, 1), dtype=np.uint8)
        arr_flipped = fliplib._fliplr_cv2(arr)
        assert arr_flipped.dtype.name == "uint8"
        assert arr_flipped.shape == (4, 0, 1)

    def test_zero_width_arr_sliced(self):
        arr = np.zeros((4, 0, 1), dtype=np.uint8)
        arr_flipped = fliplib._fliplr_sliced(arr)
        assert arr_flipped.dtype.name == "uint8"
        assert arr_flipped.shape == (4, 0, 1)

    def test_bool_faithful(self):
        arr = np.array([[False, False, True]], dtype=bool)
        arr_flipped = fliplib.fliplr(arr)
        expected = np.array([[True, False, False]], dtype=bool)
        assert arr_flipped.dtype.name == "bool"
        assert arr_flipped.shape == (1, 3)
        assert np.array_equal(arr_flipped, expected)

    def test_uint_int_faithful(self):
        dts = ["uint8", "uint16", "uint32", "uint64",
               "int8", "int16", "int32", "int64"]
        for dt in dts:
            with self.subTest(dtype=dt):
                dt = np.dtype(dt)
                minv, center, maxv = iadt.get_value_range_of_dtype(dt)
                center = int(center)
                arr = np.array([[minv, center, maxv]], dtype=dt)

                arr_flipped = fliplib.fliplr(arr)

                expected = np.array([[maxv, center, minv]], dtype=dt)
                assert arr_flipped.dtype.name == dt.name
                assert arr_flipped.shape == (1, 3)
                assert np.array_equal(arr_flipped, expected)

    def test_float_faithful_to_min_max(self):
        dts = ["float16", "float32", "float64", "float128"]
        for dt in dts:
            with self.subTest(dtype=dt):
                dt = np.dtype(dt)
                minv, center, maxv = iadt.get_value_range_of_dtype(dt)
                center = int(center)
                atol = 1e-4 if dt.name == "float16" else 1e-8
                arr = np.array([[minv, center, maxv]], dtype=dt)

                arr_flipped = fliplib.fliplr(arr)

                expected = np.array([[maxv, center, minv]], dtype=dt)
                assert arr_flipped.dtype.name == dt.name
                assert arr_flipped.shape == (1, 3)
                assert np.allclose(arr_flipped, expected, rtol=0, atol=atol)

    def test_float_faithful_to_large_values(self):
        dts = ["float16", "float32", "float64", "float128"]
        values = [
            [0.01, 0.1, 1.0, 10.0**1, 10.0**2],  # float16
            [0.01, 0.1, 1.0, 10.0**1, 10.0**2, 10.0**4, 10.0**6],  # float32
            [0.01, 0.1, 1.0, 10.0**1, 10.0**2, 10.0**6, 10.0**10],  # float64
            [0.01, 0.1, 1.0, 10.0**1, 10.0**2, 10.0**7, 10.0**11],  # float128
        ]
        for dt, values_i in zip(dts, values):
            for value in values_i:
                with self.subTest(dtype=dt, value=value):
                    dt = np.dtype(dt)
                    minv, center, maxv = -value, 0.0, value
                    atol = 1e-4 if dt.name == "float16" else 1e-8
                    arr = np.array([[minv, center, maxv]], dtype=dt)

                    arr_flipped = fliplib.fliplr(arr)

                    expected = np.array([[maxv, center, minv]], dtype=dt)
                    assert arr_flipped.dtype.name == dt.name
                    assert arr_flipped.shape == (1, 3)
                    assert np.allclose(arr_flipped, expected, rtol=0, atol=atol)


def test_Flipud():
    reseed()

    base_img = np.array([[0, 0, 1],
                         [0, 0, 1],
                         [0, 1, 1]], dtype=np.uint8)
    base_img = base_img[:, :, np.newaxis]

    base_img_flipped = np.array([[0, 1, 1],
                                 [0, 0, 1],
                                 [0, 0, 1]], dtype=np.uint8)
    base_img_flipped = base_img_flipped[:, :, np.newaxis]

    images = np.array([base_img])
    images_flipped = np.array([base_img_flipped])

    keypoints = [ia.KeypointsOnImage([ia.Keypoint(x=0, y=0),
                                      ia.Keypoint(x=1, y=1),
                                      ia.Keypoint(x=2, y=2)],
                                     shape=base_img.shape)]
    keypoints_flipped = [ia.KeypointsOnImage([ia.Keypoint(x=0, y=3-0),
                                              ia.Keypoint(x=1, y=3-1),
                                              ia.Keypoint(x=2, y=3-2)],
                                             shape=base_img.shape)]

    polygons = [ia.PolygonsOnImage(
        [ia.Polygon([(0, 0), (2, 0), (2, 2)])],
        shape=base_img.shape)]
    polygons_flipped = [ia.PolygonsOnImage(
        [ia.Polygon([(0, 3-0), (2, 3-0), (2, 3-2)])],
        shape=base_img.shape)]

    # 0% chance of flip
    aug = iaa.Flipud(0)
    aug_det = aug.to_deterministic()

    for _ in sm.xrange(10):
        observed = aug.augment_images(images)
        expected = images
        assert np.array_equal(observed, expected)

        observed = aug_det.augment_images(images)
        expected = images
        assert np.array_equal(observed, expected)

        observed = aug.augment_keypoints(keypoints)
        expected = keypoints
        assert keypoints_equal(observed, expected)

        observed = aug_det.augment_keypoints(keypoints)
        expected = keypoints
        assert keypoints_equal(observed, expected)

        for aug_ in [aug, aug_det]:
            observed = aug_.augment_polygons(polygons)
            assert len(observed) == 1
            assert len(observed[0].polygons) == 1
            assert observed[0].shape == polygons[0].shape
            assert observed[0].polygons[0].exterior_almost_equals(
                polygons[0].polygons[0])
            assert observed[0].polygons[0].is_valid

    # 0% chance of flip, heatmaps
    aug = iaa.Flipud(0)
    heatmaps = HeatmapsOnImage(
        np.float32([
            [0, 0.5, 0.75],
            [0, 0.5, 0.75],
            [0.75, 0.75, 0.75],
        ]),
        shape=(3, 3, 3)
    )
    observed = aug.augment_heatmaps([heatmaps])[0]
    expected = heatmaps.get_arr()
    assert observed.shape == heatmaps.shape
    assert heatmaps.min_value - 1e-6 < observed.min_value < heatmaps.min_value + 1e-6
    assert heatmaps.max_value - 1e-6 < observed.max_value < heatmaps.max_value + 1e-6
    assert np.array_equal(observed.get_arr(), expected)

    # 0% chance of flip, segmaps
    aug = iaa.Flipud(0)
    segmaps = SegmentationMapsOnImage(
        np.int32([
            [0, 1, 2],
            [0, 1, 2],
            [2, 2, 2],
        ]),
        shape=(3, 3, 3)
    )
    observed = aug.augment_segmentation_maps([segmaps])[0]
    expected = segmaps.get_arr()
    assert observed.shape == segmaps.shape
    assert np.array_equal(observed.get_arr(), expected)

    # 100% chance of flip
    aug = iaa.Flipud(1.0)
    aug_det = aug.to_deterministic()

    for _ in sm.xrange(10):
        observed = aug.augment_images(images)
        expected = images_flipped
        assert np.array_equal(observed, expected)

        observed = aug_det.augment_images(images)
        expected = images_flipped
        assert np.array_equal(observed, expected)

        observed = aug.augment_keypoints(keypoints)
        expected = keypoints_flipped
        assert keypoints_equal(observed, expected)

        observed = aug_det.augment_keypoints(keypoints)
        expected = keypoints_flipped
        assert keypoints_equal(observed, expected)

        for aug_ in [aug, aug_det]:
            observed = aug_.augment_polygons(polygons)
            assert len(observed) == 1
            assert len(observed[0].polygons) == 1
            assert observed[0].shape == polygons[0].shape
            assert observed[0].polygons[0].exterior_almost_equals(
                polygons_flipped[0].polygons[0])
            assert observed[0].polygons[0].is_valid

    # 100% chance of flip, heatmaps
    aug = iaa.Flipud(1.0)
    heatmaps = ia.HeatmapsOnImage(
        np.float32([
            [0, 0.5, 0.75],
            [0, 0.5, 0.75],
            [0.75, 0.75, 0.75],
        ]),
        shape=(3, 3, 3)
    )
    observed = aug.augment_heatmaps([heatmaps])[0]
    expected = np.flipud(heatmaps.get_arr())
    assert observed.shape == heatmaps.shape
    assert heatmaps.min_value - 1e-6 < observed.min_value < heatmaps.min_value + 1e-6
    assert heatmaps.max_value - 1e-6 < observed.max_value < heatmaps.max_value + 1e-6
    assert np.array_equal(observed.get_arr(), expected)

    # 100% chance of flip, segmaps
    aug = iaa.Flipud(1.0)
    segmaps = SegmentationMapsOnImage(
        np.int32([
            [0, 1, 2],
            [0, 1, 2],
            [2, 2, 2],
        ]),
        shape=(3, 3, 3)
    )
    observed = aug.augment_segmentation_maps([segmaps])[0]
    expected = np.flipud(segmaps.get_arr())
    assert observed.shape == segmaps.shape
    assert np.array_equal(observed.get_arr(), expected)

    # 50% chance of flip
    aug = iaa.Flipud(0.5)
    aug_det = aug.to_deterministic()

    nb_iterations = 1000
    nb_images_flipped = 0
    nb_images_flipped_det = 0
    nb_keypoints_flipped = 0
    nb_keypoints_flipped_det = 0
    nb_polygons_flipped = 0
    nb_polygons_flipped_det = 0
    for _ in sm.xrange(nb_iterations):
        observed = aug.augment_images(images)
        if np.array_equal(observed, images_flipped):
            nb_images_flipped += 1

        observed = aug_det.augment_images(images)
        if np.array_equal(observed, images_flipped):
            nb_images_flipped_det += 1

        observed = aug.augment_keypoints(keypoints)
        if keypoints_equal(observed, keypoints_flipped):
            nb_keypoints_flipped += 1

        observed = aug_det.augment_keypoints(keypoints)
        if keypoints_equal(observed, keypoints_flipped):
            nb_keypoints_flipped_det += 1

        observed = aug.augment_polygons(polygons)
        if observed[0].polygons[0].exterior_almost_equals(
                polygons_flipped[0].polygons[0]):
            nb_polygons_flipped += 1

        observed = aug_det.augment_polygons(polygons)
        if observed[0].polygons[0].exterior_almost_equals(
                polygons_flipped[0].polygons[0]):
            nb_polygons_flipped_det += 1

    assert int(nb_iterations * 0.3) <= nb_images_flipped <= int(nb_iterations * 0.7)
    assert int(nb_iterations * 0.3) <= nb_keypoints_flipped <= int(nb_iterations * 0.7)
    assert int(nb_iterations * 0.3) <= nb_polygons_flipped <= int(nb_iterations * 0.7)
    assert nb_images_flipped_det in [0, nb_iterations]
    assert nb_keypoints_flipped_det in [0, nb_iterations]
    assert nb_polygons_flipped_det in [0, nb_iterations]

    # 50% chance of flipped, multiple images, list as input
    images_multi = [base_img, base_img]
    aug = iaa.Flipud(0.5)
    aug_det = aug.to_deterministic()
    nb_iterations = 1000
    nb_flipped_by_pos = [0] * len(images_multi)
    nb_flipped_by_pos_det = [0] * len(images_multi)
    for _ in sm.xrange(nb_iterations):
        observed = aug.augment_images(images_multi)
        for i in sm.xrange(len(images_multi)):
            if np.array_equal(observed[i], base_img_flipped):
                nb_flipped_by_pos[i] += 1

        observed = aug_det.augment_images(images_multi)
        for i in sm.xrange(len(images_multi)):
            if np.array_equal(observed[i], base_img_flipped):
                nb_flipped_by_pos_det[i] += 1

    for val in nb_flipped_by_pos:
        assert int(nb_iterations * 0.3) <= val <= int(nb_iterations * 0.7)

    for val in nb_flipped_by_pos_det:
        assert val in [0, nb_iterations]

    # test StochasticParameter as p
    aug = iaa.Flipud(p=iap.Choice([0, 1], p=[0.7, 0.3]))
    seen = [0, 0]
    for _ in sm.xrange(1000):
        observed = aug.augment_image(base_img)
        if np.array_equal(observed, base_img):
            seen[0] += 1
        elif np.array_equal(observed, base_img_flipped):
            seen[1] += 1
        else:
            assert False
    assert 700 - 75 < seen[0] < 700 + 75
    assert 300 - 75 < seen[1] < 300 + 75

    # test exceptions for wrong parameter types
    got_exception = False
    try:
        _ = iaa.Flipud(p="test")
    except Exception:
        got_exception = True
    assert got_exception

    # test get_parameters()
    aug = iaa.Flipud(p=0.5)
    params = aug.get_parameters()
    assert isinstance(params[0], iap.Binomial)
    assert isinstance(params[0].p, iap.Deterministic)
    assert 0.5 - 1e-4 < params[0].p.value < 0.5 + 1e-4

    ###################
    # test other dtypes
    ###################
    aug = iaa.Flipud(1.0)

    image = np.zeros((3, 3), dtype=bool)
    image[0, 0] = True
    expected = np.zeros((3, 3), dtype=bool)
    expected[2, 0] = True
    image_aug = aug.augment_image(image)
    assert image_aug.dtype.type == image.dtype.type
    assert np.all(image_aug == expected)

    for dtype in [np.uint8, np.uint16, np.uint32, np.uint64, np.int8, np.int32, np.int64]:
        min_value, center_value, max_value = iadt.get_value_range_of_dtype(dtype)
        value = max_value
        image = np.zeros((3, 3), dtype=dtype)
        image[0, 0] = value
        expected = np.zeros((3, 3), dtype=dtype)
        expected[2, 0] = value
        image_aug = aug.augment_image(image)
        assert image_aug.dtype.type == dtype
        assert np.array_equal(image_aug, expected)

    for dtype, value in zip([np.float16, np.float32, np.float64, np.float128], [5000, 1000 ** 2, 1000 ** 3, 1000 ** 4]):
        atol = 1e-9 * max_value if dtype != np.float16 else 1e-3 * max_value
        image = np.zeros((3, 3), dtype=dtype)
        image[0, 0] = value
        expected = np.zeros((3, 3), dtype=dtype)
        expected[2, 0] = value
        image_aug = aug.augment_image(image)
        assert image_aug.dtype.type == dtype
        assert np.allclose(image_aug, expected, atol=atol)


if __name__ == "__main__":
    main()
