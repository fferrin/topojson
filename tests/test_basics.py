import unittest

from topojson import bounds, cut, delta, extract, geometry, join, prequantize


class BoundsTestCase(unittest.TestCase):
    def setUp(self):
        self.bbox = bounds.BoundingBox()

    def test_bounds_computes_bounding_box(self):
        foo = {
            'bar': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [0, 2], [0, 0]]
            }
        }

        self.assertCountEqual(self.bbox(foo), [0, 0, 1, 2])

    def test_bounds_considers_points_as_well_as_arcs(self):
        foo = {
            'bar': {
                'type': 'MultiPoint',
                'coordinates': [[0, 0], [1, 0], [0, 2], [0, 0]]
            }
        }

        self.assertCountEqual(self.bbox(foo), [0, 0, 1, 2])


class CutTestCase(unittest.TestCase):

    def setUp(self):
        self.cut = cut.Cut()
        self.extract = extract.Extract()

    def test_cut_exact_duplicate_lines_abc_and_abc_have_no_cuts(self):
        e = self.extract({
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'abc2': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abc': {
                'type': 'LineString',
                'arcs': {
                    0: 0,
                    1: 2
                }
            },
            'abc2': {
                'type': 'LineString',
                'arcs': {
                    0: 3,
                    1: 5
                }
            }
        }, c['objects'])

    def test_cut_reversed_duplicate_lines_abc_and_cba_have_no_cuts(self):
        e = self.extract({
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'cba': {
                'type': 'LineString',
                'arcs': [[2, 0], [1, 0], [0, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abc': {
                'type': 'LineString',
                'arcs': {
                    0: 0,
                    1: 2
                }
            },
            'cba': {
                'type': 'LineString',
                'arcs': {
                    0: 3,
                    1: 5
                }
            }
        }, c['objects'])

    def test_cut_exact_duplicate_rings_abca_and_abca_have_no_cuts(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [2, 0], [0, 0]]]
            },
            'abca2': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [2, 0], [1, 0], [0, 0]]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abca': {
                'type': 'Polygon',
                'arcs': [{0: 0, 1: 3}]
            },
            'abca2': {
                'type': 'Polygon',
                'arcs': [{0: 4, 1: 7}]
            }
        }, c['objects'])

    def test_cut_reversed_duplicate_rings_acba_and_abca_have_no_cuts(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [2, 0], [0, 0]]]
            },
            'acba': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [2, 0], [1, 0], [0, 0]]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abca': {
                'type': 'Polygon',
                'arcs': [{0: 0, 1: 3}]
            },
            'acba': {
                'type': 'Polygon',
                'arcs': [{0: 4, 1: 7}]
            }
        }, c['objects'])

    def test_cut_rotated_duplicate_rings_bcab_and_abca_have_no_cuts(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [2, 0], [0, 0]]]
            },
            'bcab': {
                'type': 'Polygon',
                'arcs': [[[1, 0], [2, 0], [0, 0], [1, 0]]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abca': {
                'type': 'Polygon',
                'arcs': [{0: 0, 1: 3}]
            },
            'bcab': {
                'type': 'Polygon',
                'arcs': [{0: 4, 1: 7}]
            }
        }, c['objects'])

    def test_cut_ring_abca_and_line_abca_have_no_cuts(self):
        e = self.extract({
            'abcaLine': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0], [0, 0]]
            },
            'abcaPolygon': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [2, 0], [0, 0]]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abcaLine': {
                'type': 'LineString',
                'arcs': [{0: 0, 1: 3}]
            },
            'abcaPolygon': {
                'type': 'Polygon',
                'arcs': [{0: 4, 1: 7}]
            }
        }, c['objects'])

    def test_cut_ring_bcab_and_line_abca_have_no_cuts(self):
        e = self.extract({
            'abcaLine': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0], [0, 0]]
            },
            'bcabPolygon': {
                'type': 'Polygon',
                'arcs': [[[1, 0], [2, 0], [0, 0], [1, 0]]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abcaLine': {
                'type': 'LineString',
                'arcs': [{0: 0, 1: 3}]
            },
            'bcabPolygon': {
                'type': 'Polygon',
                'arcs': [{0: 4, 1: 7}]
            }
        }, c['objects'])

    def test_cut_ring_abca_and_line_bcab_have_no_cuts(self):
        e = self.extract({
            'bcabLine': {
                'type': 'LineString',
                'arcs': [[1, 0], [2, 0], [0, 0], [1, 0]]
            },
            'abcaPolygon': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [2, 0], [0, 0]]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'bcabLine': {
                'type': 'LineString',
                'arcs': [{0: 0, 1: 3}]
            },
            'abcaPolygon': {
                'type': 'Polygon',
                'arcs': [{0: 4, 1: 7}]
            }
        }, c['objects'])

    def test_cut_when_an_old_arc_abc_extends_a_new_arc_ab_abc_is_cut_into_ab_bc(self):
        e = self.extract({
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'ab': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abc': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 1, 'next': {0: 1, 1: 2}}
            },
            'ab': {
                'type': 'LineString',
                'arcs': {0: 3, 1: 4}
            }
        }, c['objects'])

    def test_cut_when_a_reversed_old_arc_cba_extends_a_new_arc_ab_cba_is_cut_into_cb_ba(self):
        e = self.extract({
            'cba': {
                'type': 'LineString',
                'arcs': [[2, 0], [1, 0], [0, 0]]
            },
            'ab': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'cba': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 1, 'next': {0: 1, 1: 2}}
            },
            'ab': {
                'type': 'LineString',
                'arcs': {0: 3, 1: 4}
            }
        }, c['objects'])

    def test_cut_when_a_new_arc_ade_shares_its_start_with_an_old_arc_abc_there_are_no_cuts(self):
        e = self.extract({
            'ade': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 1], [2, 1]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'ade': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 2}
            },
            'abc': {
                'type': 'LineString',
                'arcs': {0: 3, 1: 5}
            }
        }, c['objects'])

    def test_cut_ring_aba_has_no_cuts(self):
        e = self.extract({
            'aba': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 0]]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'aba': {
                'type': 'Polygon',
                'arcs': [{0: 0, 1: 2}]
            }
        }, c['objects'])

    def test_cut_ring_aa_has_no_cuts(self):
        e = self.extract({
            'aa': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [0, 0]]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'aa': {
                'type': 'Polygon',
                'arcs': [{0: 0, 1: 1}]
            }
        }, c['objects'])

    def test_cut_degenerate_ring_a_has_no_cuts(self):
        e = self.extract({
            'a': {
                'type': 'Polygon',
                'arcs': [[[0, 0]]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'a': {
                'type': 'Polygon',
                'arcs': [{0: 0, 1: 0}]
            }
        }, c['objects'])

    def test_cut_when_a_new_line_dec_shares_its_end_with_an_old_line_abc_there_are_no_cuts(self):
        e = self.extract({
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'dec': {
                'type': 'LineString',
                'arcs': [[0, 1], [1, 1], [2, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abc': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 2}
            },
            'dec': {
                'type': 'LineString',
                'arcs': {0: 3, 1: 5}
            }
        }, c['objects'])

    def test_cut_when_a_new_line_abc_extends_an_old_line_ab_abc_is_cut_into_ab_bc(self):
        e = self.extract({
            'ab': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0]]
            },
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'ab': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 1}
            },
            'abc': {
                'type': 'LineString',
                'arcs': {0: 2, 1: 3, 'next': {0: 3, 1: 4}}
            }
        }, c['objects'])

    def test_cut_when_a_new_line_abc_extends_a_reversed_old_line_ba_abc_is_cut_into_ab_bc(self):
        e = self.extract({
            'ba': {
                'type': 'LineString',
                'arcs': [[1, 0], [0, 0]]
            },
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'ba': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 1}
            },
            'abc': {
                'type': 'LineString',
                'arcs': {0: 2, 1: 3, 'next': {0: 3, 1: 4}}
            }
        }, c['objects'])

    def test_cut_when_a_new_line_starts_bc_in_the_middle_of_an_old_line_abc_abc_is_cut_into_ab_bc(self):
        e = self.extract({
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'bc': {
                'type': 'LineString',
                'arcs': [[1, 0], [2, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abc': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 1, 'next': {0: 1, 1: 2}}
            },
            'bc': {
                'type': 'LineString',
                'arcs': {0: 3, 1: 4}
            }
        }, c['objects'])

    def test_cut_when_a_new_line_bc_starts_in_the_middle_of_a_reversed_old_line_cba_cba_is_cut_into_cb_ba(self):
        e = self.extract({
            'cba': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'bc': {
                'type': 'LineString',
                'arcs': [[1, 0], [2, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'cba': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 1, 'next': {0: 1, 1: 2}}
            },
            'bc': {
                'type': 'LineString',
                'arcs': {0: 3, 1: 4}
            }
        }, c['objects'])

    def test_cut_when_a_new_line_abd_deviates_from_an_old_line_abc_abd_is_cut_into_ab_bd_and_abc_is_cut_into_ab_bc(self):
        e = self.extract({
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'abd': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [3, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abc': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 1, 'next': {0: 1, 1: 2}}
            },
            'abd': {
                'type': 'LineString',
                'arcs': {0: 3, 1: 4, 'next': {0: 4, 1: 5}}
            }
        }, c['objects'])

    def test_cut_when_a_new_line_abd_deviates_from_a_reversed_old_line_cba_cba_is_cut_into_cb_ba_and_abd_is_cut_into_ab_bd(self):
        e = self.extract({
            'cba': {
                'type': 'LineString',
                'arcs': [[2, 0], [1, 0], [0, 0]]
            },
            'abd': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [3, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'cba': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 1, 'next': {0: 1, 1: 2}}
            },
            'abd': {
                'type': 'LineString',
                'arcs': {0: 3, 1: 4, 'next': {0: 4, 1: 5}}
            }
        }, c['objects'])

    def test_cut_when_a_new_line_dbc_merges_into_an_old_line_abc_dbc_is_cut_into_db_bc_and_abc_is_cut_into_ab_bc(self):
        e = self.extract({
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'dbc': {
                'type': 'LineString',
                'arcs': [[3, 0], [1, 0], [2, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abc': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 1, 'next': {0: 1, 1: 2}}
            },
            'dbc': {
                'type': 'LineString',
                'arcs': {0: 3, 1: 4, 'next': {0: 4, 1: 5}}
            }
        }, c['objects'])

    def test_cut_when_a_new_line_dbc_merges_into_a_reversed_old_line_cba_dbc_is_cut_into_db_bc_and_cba_is_cut_into_cb_ba(self):
        e = self.extract({
            'cba': {
                'type': 'LineString',
                'arcs': [[2, 0], [1, 0], [0, 0]]
            },
            'dbc': {
                'type': 'LineString',
                'arcs': [[3, 0], [1, 0], [2, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'cba': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 1, 'next': {0: 1, 1: 2}}
            },
            'dbc': {
                'type': 'LineString',
                'arcs': {0: 3, 1: 4, 'next': {0: 4, 1: 5}}
            }
        }, c['objects'])

    def test_cut_when_a_new_line_dbe_shares_a_single_midpoint_with_an_old_line_abc_dbe_is_cut_into_db_be_and_abc_is_cut_into_ab_bc(self):
        e = self.extract({
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'dbe': {
                'type': 'LineString',
                'arcs': [[0, 1], [1, 0], [2, 1]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abc': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 1, 'next': {0: 1, 1: 2}}
            },
            'dbe': {
                'type': 'LineString',
                'arcs': {0: 3, 1: 4, 'next': {0: 4, 1: 5}}
            }
        }, c['objects'])

    def test_cut_when_a_new_line_abde_skips_a_point_with_an_old_line_abcde_abde_is_cut_into_ab_bd_de_and_abcde_is_cut_into_ab_bcd_de(self):
        e = self.extract({
            'abcde': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]]
            },
            'abde': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [3, 0], [4, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abcde': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 1, 'next': {0: 1, 1: 3, 'next': {0: 3, 1: 4}}}
            },
            'abde': {
                'type': 'LineString',
                'arcs': {0: 5, 1: 6, 'next': {0: 6, 1: 7, 'next': {0: 7, 1: 8}}}
            }
        }, c['objects'])

    def test_cut_when_a_new_line_abde_skips_a_point_with_a_reversed_old_line_edcba_abde_is_cut_into_ab_bd_de_and_edcba_is_cut_into_ed_dcb_ba(self):
        e = self.extract({
            'edcba': {
                'type': 'LineString',
                'arcs': [[4, 0], [3, 0], [2, 0], [1, 0], [0, 0]]
            },
            'abde': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [3, 0], [4, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'edcba': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 1, 'next': {0: 1, 1: 3, 'next': {0: 3, 1: 4}}}
            },
            'abde': {
                'type': 'LineString',
                'arcs': {0: 5, 1: 6, 'next': {0: 6, 1: 7, 'next': {0: 7, 1: 8}}}
            }
        }, c['objects'])

    def test_cut_when_a_line_abcdbe_self_intersects_with_its_middle_it_is_not_cut(self):
        e = self.extract({
            'abcdbe': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0], [3, 0], [1, 0], [4, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abcdbe': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 5}
            }
        }, c['objects'])

    def test_cut_when_a_line_abacd_self_intersects_with_its_start_it_is_cut_into_aba_acd(self):
        e = self.extract({
            'abacd': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [0, 0], [3, 0], [4, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abacd': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 2, 'next': {0: 2, 1: 4}}
            }
        }, c['objects'])

    def test_cut_when_a_line_abdcd_self_intersects_with_its_end_it_is_cut_into_abd_dcd(self):
        e = self.extract({
            'abdcd': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [0, 0], [3, 0], [4, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abdcd': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 2, 'next': {0: 2, 1: 4}}
            }
        }, c['objects'])

    def test_cut_when_an_old_line_abcdbe_self_intersects_and_shares_a_point_b_abcdbe_is_cut_into_ab_bcdb_be_and_fbg_is_cut_into_fb_bg(self):
        e = self.extract({
            'abcdbe': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0], [3, 0], [1, 0], [4, 0]]
            },
            'fbg': {
                'type': 'LineString',
                'arcs': [[0, 1], [1, 0], [2, 1]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abcdbe': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 1, 'next': {0: 1, 1: 4, 'next': {0: 4, 1: 5}}}
            },
            'fbg': {
                'type': 'LineString',
                'arcs': {0: 6, 1: 7, 'next': {0: 7, 1: 8}}
            }
        }, c['objects'])

    def test_cut_when_a_line_abca_is_closed_there_are_no_cuts(self):
        e = self.extract({
            'abca': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [0, 1], [0, 0]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abca': {
                'type': 'LineString',
                'arcs': {0: 0, 1: 3}
            }
        }, c['objects'])

    def test_cut_when_a_ring_abca_is_closed_there_are_no_cuts(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 1], [0, 0]]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abca': {
                'type': 'Polygon',
                'arcs': [{0: 0, 1: 3}]
            }
        }, c['objects'])

    def test_cut_exact_duplicate_rings_abca_and_abca_have_no_cuts(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 1], [0, 0]]]
            },
            'abca2': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 1], [0, 0]]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abca': {
                'type': 'Polygon',
                'arcs': [{0: 0, 1: 3}]
            },
            'abca2': {
                'type': 'Polygon',
                'arcs': [{0: 4, 1: 7}]
            }
        }, c['objects'])

    def test_cut_reversed_duplicate_rings_abca_and_acba_have_no_cuts(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 1], [0, 0]]]
            },
            'acba': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [0, 1], [1, 0], [0, 0]]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abca': {
                'type': 'Polygon',
                'arcs': [{0: 0, 1: 3}]
            },
            'acba': {
                'type': 'Polygon',
                'arcs': [{0: 4, 1: 7}]
            }
        }, c['objects'])

    def test_cut_coincident_rings_abca_and_bcab_have_no_cuts(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 1], [0, 0]]]
            },
            'bcab': {
                'type': 'Polygon',
                'arcs': [[[1, 0], [0, 1], [0, 0], [1, 0]]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abca': {
                'type': 'Polygon',
                'arcs': [{0: 0, 1: 3}]
            },
            'bcab': {
                'type': 'Polygon',
                'arcs': [{0: 4, 1: 7}]
            }
        }, c['objects'])

    def test_cut_coincident_rings_abca_and_bacb_have_no_cuts(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 1], [0, 0]]]
            },
            'bacb': {
                'type': 'Polygon',
                'arcs': [[[1, 0], [0, 0], [0, 1], [1, 0]]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abca': {
                'type': 'Polygon',
                'arcs': [{0: 0, 1: 3}]
            },
            'bacb': {
                'type': 'Polygon',
                'arcs': [{0: 4, 1: 7}]
            }
        }, c['objects'])

    def test_cut_coincident_rings_abca_and_dbed_have_no_cuts_but_are_rotated_to_share_b(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 1], [0, 0]]]
            },
            'dbed': {
                'type': 'Polygon',
                'arcs': [[[2, 1], [1, 0], [2, 2], [2, 1]]]
            }
        })

        topology = self.cut(e)

        self.assertDictEqual({
            'abca': {
                'type': 'Polygon',
                'arcs': [{0: 0, 1: 3}]
            },
            'dbed': {
                'type': 'Polygon',
                'arcs': [{0: 4, 1: 7}]
            }
        }, topology['objects'])

        self.assertCountEqual(topology['coordinates'][0:4], [[1, 0], [0, 1], [0, 0], [1, 0]])
        self.assertCountEqual(topology['coordinates'][4:8], [[1, 0], [2, 2], [2, 1], [1, 0]])

    def test_cut_overlapping_rings_abcda_and_befcb_are_cut_into_bc_cdab_and_befc_cb(self):
        e = self.extract({
            'abcda': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]] # rotated to BCDAB, cut BC-CDAB
            },
            'befcb': {
                'type': 'Polygon',
                'arcs': [[[1, 0], [2, 0], [2, 1], [1, 1], [1, 0]]]
            }
        })

        c = self.cut(e)

        self.assertDictEqual({
            'abcda': {
                'type': 'Polygon',
                'arcs': [{0: 0, 1: 1, 'next': {0: 1, 1: 4}}]
            },
            'befcb': {
                'type': 'Polygon',
                'arcs': [{0: 5, 1: 8, 'next': {0: 8, 1: 9}}]
            }
        }, c['objects'])


class DeltaTestCase(unittest.TestCase):

    def setUp(self):
        self.delta = delta.Delta()

    def test_delta_converts_arcs_to_delta_encoding(self):
        d = self.delta([
            [[0, 0], [9999, 0], [0, 9999], [0, 0]]
        ])

        self.assertCountEqual(
            d,
            [
                [[0, 0], [9999, 0], [-9999, 9999], [0, -9999]]
            ]
        )

    def test_delta_skips_coincident_points(self):
        d = self.delta([
            [[0, 0], [9999, 0], [9999, 0], [0, 9999], [0, 0]]
        ])

        self.assertCountEqual(
            d,
            [
                [[0, 0], [9999, 0], [-9999, 9999], [0, -9999]]
            ]
        )

    def test_delta_preserves_at_least_two_positions(self):
        d = self.delta([
            [[12345, 12345], [12345, 12345], [12345, 12345], [12345, 12345]]
        ])

        self.assertCountEqual(
            d,
            [
                [[12345, 12345], [0, 0]]
            ]
        )


class ExtractTestCase(unittest.TestCase):

    def setUp(self):
        self.extract = extract.Extract()

    def test_extract_copies_coordinates_sequentially_into_a_buffer(self):
        topology = self.extract({
            'foo': {
                'type': "LineString",
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'bar': {
                'type': "LineString",
                'arcs': [[0, 0], [1, 0], [2, 0]]
            }
        })

        self.assertCountEqual(topology['coordinates'], [[0, 0], [1, 0], [2, 0], [0, 0], [1, 0], [2, 0]])

    def test_extract_does_not_copy_point_geometries_into_the_coordinate_buffer(self):
        topology = self.extract({
            'foo': {
                'type': 'Point',
                'arcs': [0, 0]
            },
            'bar': {
                'type': 'MultiPoint',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            }
        })

        self.assertCountEqual(topology['coordinates'], [])
        self.assertCountEqual(topology['objects']['foo']['arcs'], [0, 0])
        self.assertCountEqual(topology['objects']['bar']['arcs'], [[0, 0], [1, 0], [2, 0]])

    def test_extract_includes_closing_coordinates_in_polygons(self):
        topology = self.extract({
            'foo': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [2, 0], [0, 0]]]
            }
        })

        self.assertCountEqual(topology['coordinates'], [[0, 0], [1, 0], [2, 0], [0, 0]])

    def test_extract_represents_lines_as_contiguous_slices_of_the_coordinate_buffer(self):
        topology = self.extract({
            'foo': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'bar': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            }
        })

        self.assertDictEqual(
            topology['objects'],
            {
                'foo': {
                    'type': 'LineString',
                    'arcs': [0, 2]
                },
                'bar': {
                    'type': 'LineString',
                    'arcs': [3, 5]
                }
            }
        )

    def test_extract_represents_rings_as_contiguous_slices_of_the_coordinate_buffer(self):
        topology = self.extract({
            'foo': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [2, 0], [0, 0]]]
            },
            'bar': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [2, 0], [0, 0]]]
            }
        })

        self.assertDictEqual(
            topology['objects'],
            {
                'foo': {
                    'type': 'Polygon',
                    'arcs': [[0, 3]]
                },
                'bar': {
                    'type': 'Polygon',
                    'arcs': [[4, 7]]
                }
            }
        )

    def test_extract_exposes_the_constructed_lines_and_rings_in_the_order_of_construction(self):
        topology = self.extract({
            'line': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'multiline': {
                'type': 'MultiLineString',
                'arcs': [[[0, 0], [1, 0], [2, 0]]]
            },
            'polygon': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [2, 0], [0, 0]]]
            }
        })

        self.assertCountEqual(topology['lines'], [[0, 2], [3, 5]])
        self.assertCountEqual(topology['rings'], [[6, 9]])

    def test_extract_supports_nested_geometry_collections(self):
        topology = self.extract({
            'foo': {
                'type': 'GeometryCollection',
                'geometries': [{
                    'type': 'GeometryCollection',
                    'geometries': [{
                        'type': 'LineString',
                        'arcs': [[0, 0], [0, 1]]
                    }]
                }]
            }
        })

        self.assertDictEqual(
            topology['objects']['foo'],
            {
                'type': 'GeometryCollection',
                'geometries': [{
                    'type': 'GeometryCollection',
                    'geometries': [{
                        'type': 'LineString',
                        'arcs': [0, 1]
                    }]
                }]
            }

        )


class GeometryTestCase(unittest.TestCase):
    def setUp(self):
        self.geometry = geometry.Geometry()

    def test_geometry_replaces_LineString_Feature_with_LineString_Geometry(self):
        geom = self.geometry({
            'foo': {
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [[0, 0]]
                }
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'type': 'LineString',
                    'arcs': [[0, 0]]
                }
            }
        )

    def test_geometry_replaces_GeometryCollection_Feature_with_GeometryCollection(self):
        geom = self.geometry({
            'foo': {
                'type': 'Feature',
                'geometry': {
                    'type': 'GeometryCollection',
                    'geometries': [{
                        'type': 'LineString',
                        'coordinates': [[0, 0]]
                    }]
                }
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'type': 'GeometryCollection',
                    'geometries': [{
                        'type': 'LineString',
                        'arcs': [[0, 0]]
                    }]
                }
            }
        )

    def test_geometry_replaces_FeatureCollection_with_GeometryCollection(self):
        geom = self.geometry({
            'foo': {
                'type': 'FeatureCollection',
                'features': [{
                    'type': 'Feature',
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': [[0, 0]]
                    }
                }]
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'type': 'GeometryCollection',
                    'geometries': [{
                        'type': 'LineString',
                        'arcs': [[0, 0]]
                    }]
                }
            }
        )

    def test_geometry_replaces_Feature_with_null_Geometry_with_null_type_Geometry(self):
        geom = self.geometry({
            'foo': {
                'type': 'Feature',
                'geometry': None
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'type': None
                }
            }
        )

    def test_geometry_replaces_top_level_null_Geometry_with_null_type_Geometry(self):
        geom = self.geometry({
            'foo': None
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'type': None
                }
            }
        )

    def test_geometry_replaces_null_Geometry_in_GeometryCollection_with_null_type_Geometry(self):
        geom = self.geometry({
            'foo': {
                'type': 'GeometryCollection',
                'geometries': [None]
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'type': 'GeometryCollection',
                    'geometries': [{
                        'type': None
                    }]
                }
            }
        )

    def test_geometry_preserves_id(self):
        geom = self.geometry({
            'foo': {
                'id': 'foo',
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [[0, 0]]
                }
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'id': 'foo',
                    'type': 'LineString',
                    'arcs': [[0, 0]]
                }
            }
        )

    def test_geometry_preserves_properties_if_non_empty(self):
        geom = self.geometry({
            'foo': {
                'properties': {
                    'foo': 42
                },
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [[0, 0]]
                }
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'properties': {
                        'foo': 42
                    },
                    'type': 'LineString',
                    'arcs': [[0, 0]]
                }
            }
        )

    def test_geometry_applies_a_shallow_copy_for_properties(self):
        input = {
            'foo': {
                'properties': {
                    'foo': 42
                },
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [[0, 0]]
                }
            }
        }

        geom = self.geometry(input)

        self.assertDictEqual(input['foo']['properties'], geom['foo']['properties'])

    def test_geometry_deletes_empty_properties(self):
        geom = self.geometry({
            'foo': {
                'properties': {},
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [[0, 0]]
                }
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'type': 'LineString',
                    'arcs': [[0, 0]]
                }
            }
        )

    def test_geometry_does_not_convert_singular_multipoints_to_points(self):
        geom = self.geometry({
            'foo': {
                'type': 'MultiPoint',
                'coordinates': [[0, 0]]
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'type': 'MultiPoint',
                    'coordinates': [[0, 0]]
                }
            }
        )

    def test_geometry_does_not_convert_empty_multipoints_to_null(self):
        geom = self.geometry({
            'foo': {
                'type': 'MultiPoint',
                'coordinates': []
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'type': 'MultiPoint',
                    'coordinates': []
                }
            }
        )

    def test_geometry_does_not_convert_singular_multilines_to_line(self):
        geom = self.geometry({
            'foo': {
                'type': 'MultiLineString',
                'coordinates': [[[0, 0], [0, 1]]]
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'type': 'MultiLineString',
                    'arcs': [[[0, 0], [0, 1]]]
                }
            }
        )

    def test_geometry_does_not_convert_empty_lines_to_null(self):
        geom = self.geometry({
            'foo': {
                'type': 'LineString',
                'coordinates': []
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'type': 'LineString',
                    'arcs': []
                }
            }
        )

    def test_geometry_does_not_convert_empty_multilines_to_null(self):
        geom = self.geometry({
            'foo': {
                'type': 'MultiLineString',
                'coordinates': []
            },
            'bar': {
                'type': 'MultiLineString',
                'coordinates': [[]]
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'type': 'MultiLineString',
                    'arcs': []
                },
                'bar': {
                    'type': 'MultiLineString',
                    'arcs': [[]]
                }
            }
        )

    def test_geometry_does_not_strip_empty_lines_in_multilines(self):
        geom = self.geometry({
            'foo': {
                'type': 'MultiLineString',
                'coordinates': [[[0, 0], [1, 0], [1, 1], [0, 0]], [], [[0, 0], [1, 0]]]
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'type': 'MultiLineString',
                    'arcs': [[[0, 0], [1, 0], [1, 1], [0, 0]], [], [[0, 0], [1, 0]]]
                }
            }
        )

    def test_geometry_does_not_convert_empty_polygons_to_null(self):
        geom = self.geometry({
            'foo': {
                'type': 'Polygon',
                'coordinates': []
            },
            'bar': {
                'type': 'Polygon',
                'coordinates': [[]]
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'type': 'Polygon',
                    'arcs': []
                },
                'bar': {
                    'type': 'Polygon',
                    'arcs': [[]]
                }
            }
        )

    def test_geometry_does_not_strip_empty_polygons_in_multipolygons(self):
        geom = self.geometry({
            'foo': {
                'type': 'MultiPolygon',
                'coordinates': [[[[0, 0], [1, 0], [1, 1], [0, 0]], []], [], [[]]]
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'type': 'MultiPolygon',
                    'arcs': [[[[0, 0], [1, 0], [1, 1], [0, 0]], []], [], [[]]]
                }
            }
        )

    def test_geometry_does_not_convert_singular_multipolygons_to_polygons(self):
        geom = self.geometry({
            'foo': {
                'type': 'MultiPolygon',
                'coordinates': [[[[0, 0], [0, 1], [1, 0], [0, 0]]]]
            }
        })

        self.assertDictEqual(
            geom,
            {
                'foo': {
                    'type': 'MultiPolygon',
                    'arcs': [[[[0, 0], [0, 1], [1, 0], [0, 0]]]]
                }
            }
        )


class JoinTestCase(unittest.TestCase):

    def setUp(self):
        self.extract = extract.Extract()
        self.join = join.Join()

    def test_join_the_returned_hashmap_has_true_for_junction_points(self):
        e = self.extract({
            'cba': {
                'type': 'LineString',
                'arcs': [[2, 0], [1, 0], [0, 0]]
            },
            'ab': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0]]
            }
        })
        junctions = self.join(e)

        self.assertEquals(junctions.has([2, 0]), True)
        self.assertEquals(junctions.has([0, 0]), True)

    def test_join_the_returned_hashmap_undefined_for_non_junction_points(self):
        e = self.extract({
            'cba': {
                'type': 'LineString',
                'arcs': [[2, 0], [1, 0], [0, 0]]
            },
            'ab': {
                'type': 'LineString',
                'arcs': [[0, 0], [2, 0]]
            }
        })
        junctions = self.join(e)

        self.assertEquals(junctions.has([1, 0]), False)

    def test_join_exact_duplicate_lines_abc_and_abc_have_junctions_at_their_end_points(self):
        e = self.extract({
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'abc2': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [2, 0]])

    def test_join_reversed_duplicate_lines_abc_and_cba_have_junctions_at_their_end_points(self):
        e = self.extract({
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'cba': {
                'type': 'LineString',
                'arcs': [[2, 0], [1, 0], [0, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [2, 0]])

    def test_join_exact_duplicate_rings_abca_and_abca_have_no_junctions(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [2, 0], [0, 0]]]
            },
            'abca2': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [2, 0], [0, 0]]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [])

    def test_join_reversed_duplicate_rings_abca_and_abca_have_no_junctions(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [2, 0], [0, 0]]]
            },
            'acba': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [2, 0], [1, 0], [0, 0]]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [])

    def test_join_rotated_duplicate_rings_abca_and_abca_have_no_junctions(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [2, 0], [0, 0]]]
            },
            'bcab': {
                'type': 'Polygon',
                'arcs': [[[1, 0], [2, 0], [0, 0], [1, 0]]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [])

    def test_join_ring_abca_and_abca_have_a_junction_at_a(self):
        e = self.extract({
            'abcaLine': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0], [0, 0]]
            },
            'abcaPolygon': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [2, 0], [0, 0]]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0]])

    def test_join_ring_bcab_and_abca_have_a_junction_at_a(self):
        e = self.extract({
            'abcaLine': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0], [0, 0]]
            },
            'bcabPolygon': {
                'type': 'Polygon',
                'arcs': [[[1, 0], [2, 0], [0, 0], [1, 0]]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0]])

    def test_join_ring_abca_and_bcab_have_a_junction_at_b(self):
        e = self.extract({
            'bcabLine': {
                'type': 'LineString',
                'arcs': [[1, 0], [2, 0], [0, 0], [1, 0]]
            },
            'abcaPolygon': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [2, 0], [0, 0]]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[1, 0]])

    def test_join_when_an_old_arc_abc_extends_a_new_arc_ab_there_is_a_junction_at_b(self):
        e = self.extract({
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'ab': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [1, 0], [2, 0]])

    def test_join_when_a_reversed_old_arc_cba_extends_a_new_arc_ab_there_is_a_junction_at_b(self):
        e = self.extract({
            'cba': {
                'type': 'LineString',
                'arcs': [[2, 0], [1, 0], [0, 0]]
            },
            'ab': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [1, 0], [2, 0]])

    def test_join_join_when_a_new_arc_ade_shares_its_start_with_an_old_arc_abc_there_is_a_junction_at_a(self):
        e = self.extract({
            'ade': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 1], [2, 1]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [2, 0], [2, 1]])

    def test_join_ring_aba_has_no_junctions(self):
        e = self.extract({
            'aba': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 0]]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [])

    def test_join_ring_aa_has_no_junctions(self):
        e = self.extract({
            'aa': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [0, 0]]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [])

    def test_join_degenerate_ring_a_has_no_junctions(self):
        e = self.extract({
            'a': {
                'type': 'Polygon',
                'arcs': [[[0, 0]]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [])

    def test_join_when_a_new_line_dec_shares_its_end_with_an_old_line_abc_there_is_a_junction_at_c(self):
        e = self.extract({
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'dec': {
                'type': 'LineString',
                'arcs': [[0, 1], [1, 1], [2, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [2, 0], [0, 1]])

    def test_join_when_a_new_line_abc_extends_an_old_line_ab_there_is_a_junction_at_b(self):
        e = self.extract({
            'ab': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0]]
            },
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [1, 0], [2, 0]])

    def test_join_when_a_new_line_abc_extends_a_reversed_old_line_ba_there_is_a_junction_at_b(self):
        e = self.extract({
            'ba': {
                'type': 'LineString',
                'arcs': [[1, 0], [0, 0]]
            },
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [1, 0], [2, 0]])

    def test_join_when_a_new_line_starts_bc_in_the_middle_of_an_old_line_abc_there_is_a_junction_at_b(self):
        e = self.extract({
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'bc': {
                'type': 'LineString',
                'arcs': [[1, 0], [2, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [1, 0], [2, 0]])

    def test_join_when_a_new_line_bc_starts_in_the_middle_of_a_reversed_old_line_cba_there_is_a_junction_at_b(self):
        e = self.extract({
            'cba': {
                'type': 'LineString',
                'arcs': [[2, 0], [1, 0], [0, 0]]
            },
            'bc': {
                'type': 'LineString',
                'arcs': [[1, 0], [2, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [1, 0], [2, 0]])

    def test_join_when_a_new_line_abd_deviates_from_an_old_line_abc_there_is_a_junction_at_b(self):
        e = self.extract({
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'abd': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [3, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [2, 0], [1, 0], [3, 0]])

    def test_join_when_a_new_line_abd_deviates_from_a_reversed_old_line_cba_there_is_a_junction_at_b(self):
        e = self.extract({
            'cba': {
                'type': 'LineString',
                'arcs': [[2, 0], [1, 0], [0, 0]]
            },
            'abd': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [3, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[2, 0], [0, 0], [1, 0], [3, 0]])

    def test_join_when_a_new_line_dbc_merges_into_an_old_line_abc_there_is_a_junction_at_b(self):
        e = self.extract({
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'dbc': {
                'type': 'LineString',
                'arcs': [[3, 0], [1, 0], [2, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [2, 0], [1, 0], [3, 0]])

    def test_join_when_a_new_line_dbc_merges_into_a_reversed_old_line_cba_there_is_a_junction_at_b(self):
        e = self.extract({
            'cba': {
                'type': 'LineString',
                'arcs': [[2, 0], [1, 0], [0, 0]]
            },
            'dbc': {
                'type': 'LineString',
                'arcs': [[3, 0], [1, 0], [2, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[2, 0], [0, 0], [1, 0], [3, 0]])

    def test_join_when_a_new_line_dbe_shares_a_single_midpoint_with_an_old_line_abc_there_is_a_junction_at_b(self):
        e = self.extract({
            'abc': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0]]
            },
            'dbe': {
                'type': 'LineString',
                'arcs': [[0, 1], [1, 0], [2, 1]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [2, 0], [2, 1], [1, 0], [0, 1]])

    def test_VER_join_when_a_new_line_dbe_shares_a_single_midpoint_with_an_old_line_abc_there_is_a_junction_at_b(self):
        e = self.extract({
            'abcde': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]]
            },
            'abde': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [3, 0], [4, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [4, 0], [1, 0], [3, 0]])

    def test_join_when_a_new_line_abde_skips_a_point_with_a_reversed_old_line_edcba_there_is_a_junction_at_b_and_d(self):
        e = self.extract({
            'edcba': {
                'type': 'LineString',
                'arcs': [[4, 0], [3, 0], [2, 0], [1, 0], [0, 0]]
            },
            'abde': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [3, 0], [4, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[4, 0], [0, 0], [1, 0], [3, 0]])

    def test_join_when_a_line_abcdbe_self_intersects_with_its_middle_there_are_no_junctions(self):
        e = self.extract({
            'abcdbe': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0], [3, 0], [1, 0], [4, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [4, 0]])

    def test_join_when_a_line_abacd_self_intersects_with_its_start_there_are_no_junctions(self):
        e = self.extract({
            'abacd': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [0, 0], [3, 0], [4, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [4, 0]])

    def test_join_when_a_line_abcdbd_self_intersects_with_its_end_there_are_no_junctions(self):
        e = self.extract({
            'abcdbd': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [4, 0], [3, 0], [4, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [4, 0]])

    def test_join_when_an_old_line_abcdbe_self_intersects_and_shares_a_point_b_there_is_a_junction_at_b(self):
        e = self.extract({
            'abcdbe': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [2, 0], [3, 0], [1, 0], [4, 0]]
            },
            'fbg': {
                'type': 'LineString',
                'arcs': [[0, 1], [1, 0], [2, 1]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0], [4, 0], [1, 0], [0, 1], [2, 1]])

    def test_join_when_a_line_abca_is_closed_there_is_a_junction_at_a(self):
        e = self.extract({
            'abca': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [0, 1], [0, 0]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[0, 0]])

    def test_join_when_a_ring_abca_is_closed_there_are_no_junctions(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 1], [0, 0]]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [])

    def test_join_exact_duplicate_rings_abca_and_abca_share_the_arc_abca(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 1], [0, 0]]]
            },
            'abca2': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 1], [0, 0]]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [])

    def test_join_reversed_duplicate_rings_abca_and_acba_share_the_arc_abca(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 1], [0, 0]]]
            },
            'acba': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [0, 1], [1, 0], [0, 0]]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [])

    def test_join_coincident_rings_abca_and_bcab_share_the_arc_bcab(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 1], [0, 0]]]
            },
            'bcab': {
                'type': 'Polygon',
                'arcs': [[[1, 0], [0, 1], [0, 0], [1, 0]]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [])

    def test_join_coincident_rings_abca_and_bacb_share_the_arc_bcab(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 1], [0, 0]]]
            },
            'bacb': {
                'type': 'Polygon',
                'arcs': [[[1, 0], [0, 0], [0, 1], [1, 0]]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [])

    def test_join_coincident_rings_abca_and_dbed_share_the_point_b(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 1], [0, 0]]]
            },
            'dbed': {
                'type': 'Polygon',
                'arcs': [[[2, 1], [1, 0], [2, 2], [2, 1]]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[1, 0]])

    def test_join_coincident_ring_abca_and_line_dbe_share_the_point_b(self):
        e = self.extract({
            'abca': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [1, 0], [0, 1], [0, 0]]]
            },
            'dbe': {
                'type': 'LineString',
                'arcs': [[2, 1], [1, 0], [2, 2]]
            }
        })
        junctions = self.join(e)

        self.assertCountEqual(junctions.values(), [[2, 1], [2, 2], [1, 0]])


class PrequantizeTestCase(unittest.TestCase):

    def setUp(self):
        self.prequantize = prequantize.Prequantize()

    def test_prequantize_returns_the_quantization_transform(self):
        quantize = self.prequantize({}, [0, 0, 1, 1], 1e4)

        self.assertDictEqual(
            quantize,
            {
                'scale': [1 / 9999, 1 / 9999],
                'translate': [0, 0]
            }
        )

    def test_prequantize_converts_coordinates_to_fixed_precision(self):
        objects = {
            'foo': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [0, 1], [0, 0]]
            }
        }

        self.prequantize(objects, [0, 0, 1, 1], 1e4)
        self.assertCountEqual(objects['foo']['arcs'], [[0, 0], [9999, 0], [0, 9999], [0, 0]])

    def test_prequantize_observes_the_quantization_parameter(self):
        objects = {
            'foo': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [0, 1], [0, 0]]
            }
        }

        self.prequantize(objects, [0, 0, 1, 1], 10)
        self.assertCountEqual(objects['foo']['arcs'], [[0, 0], [9, 0], [0, 9], [0, 0]])

    def test_prequantize_observes_the_bounding_box(self):
        objects = {
            'foo': {
                'type': 'LineString',
                'arcs': [[0, 0], [1, 0], [0, 1], [0, 0]]
            }
        }

        self.prequantize(objects, [-1, -1, 2, 2], 10)
        self.assertCountEqual(objects['foo']['arcs'], [[3, 3], [6, 3], [3, 6], [3, 3]])

    def test_prequantize_applies_to_points_as_well_as_arcs(self):
        objects = {
            'foo': {
                'type': 'MultiPoint',
                'coordinates': [[0, 0], [1, 0], [0, 1], [0, 0]]
            }
        }

        self.prequantize(objects, [0, 0, 1, 1], 1e4)
        self.assertCountEqual(objects['foo']['coordinates'], [[0, 0], [9999, 0], [0, 9999], [0, 0]])

    def test_prequantize_skips_coincident_points_in_line(self):
        objects = {
            'foo': {
                'type': 'LineString',
                'arcs': [[0, 0], [0.9, 0.9], [1.1, 1.1], [2, 2]]
            }
        }

        self.prequantize(objects, [0, 0, 2, 2], 3)
        self.assertCountEqual(objects['foo']['arcs'], [[0, 0], [1, 1], [2, 2]])

    def test_prequantize_skips_coincident_points_in_polygon(self):
        objects = {
            'foo': {
                'type': 'Polygon',
                'arcs': [[[0, 0], [0.9, 0.9], [1.1, 1.1], [2, 2], [0, 0]]]
            }
        }

        self.prequantize(objects, [0, 0, 2, 2], 3)
        self.assertCountEqual(objects['foo']['arcs'], [[[0, 0], [1, 1], [2, 2], [0, 0]]])

    def test_prequantize_does_not_skip_coincident_points_in_point(self):
        objects = {
            'foo': {
                'type': 'MultiPoint',
                'coordinates': [[0, 0], [0.9, 0.9], [1.1, 1.1], [2, 2], [0, 0]]
            }
        }

        self.prequantize(objects, [0, 0, 2, 2], 3)
        self.assertCountEqual(objects['foo']['coordinates'], [[0, 0], [1, 1], [1, 1], [2, 2], [0, 0]])

    def test_prequantize_includes_closing_point_in_degenerate_lines(self):
        objects = {
            'foo': {
                'type': 'LineString',
                'arcs': [[1, 1], [1, 1], [1, 1]]
            }
        }

        self.prequantize(objects, [0, 0, 2, 2], 3)
        self.assertCountEqual(objects['foo']['arcs'], [[1, 1], [1, 1]])

    def test_prequantize_includes_closing_point_in_degenerate_polygons(self):
        objects = {
            'foo': {
                'type': 'Polygon',
                'arcs': [[[0.9, 1], [1.1, 1], [1.01, 1], [0.9, 1]]]
            }
        }

        self.prequantize(objects, [0, 0, 2, 2], 3)
        self.assertCountEqual(objects['foo']['arcs'], [[[1, 1], [1, 1], [1, 1], [1, 1]]])


if __name__ == '__main__':
    unittest.main()
