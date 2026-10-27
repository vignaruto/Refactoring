import unittest

import pandas as pd

import train_model as tm


class ProgramSplitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = tm.load_dataset()

    def test_similarity_groups_never_cross_the_split(self):
        for fold in range(tm.N_FOLDS):
            train, test = tm.program_split(self.data, fold)
            train_groups = set(self.data.loc[train, "similarity_group"])
            test_groups = set(self.data.loc[test, "similarity_group"])
            self.assertFalse(train_groups & test_groups, f"fold {fold}")

    def test_folds_cover_every_program_once(self):
        seen = []
        for fold in range(tm.N_FOLDS):
            _, test = tm.program_split(self.data, fold)
            seen.extend(self.data.loc[test, "program_id"].unique())
        self.assertEqual(len(seen), len(set(seen)))
        self.assertEqual(set(seen), set(self.data["program_id"]))

    def test_every_category_is_in_the_test_programs(self):
        _, test = tm.program_split(self.data)
        categories = set(self.data.loc[test, "intended_category"])
        self.assertEqual(categories, set(self.data["intended_category"]))

    def test_split_is_deterministic(self):
        first = tm.program_split(self.data)[1]
        second = tm.program_split(self.data)[1]
        self.assertTrue((first == second).all())


class FeatureTests(unittest.TestCase):
    def rows(self, statement_type):
        row = {name: 1 for name in tm.NUMERIC_FEATURES}
        row["statement_type"] = statement_type
        return pd.DataFrame([row])

    def test_columns_follow_feature_order(self):
        features = tm.build_features(self.rows("For"))
        self.assertEqual(list(features.columns), tm.FEATURE_COLUMNS)
        self.assertEqual(features.loc[0, "type_For"], 1.0)
        self.assertEqual(features.loc[0, "type_If"], 0.0)

    def test_unknown_statement_type_is_rejected(self):
        with self.assertRaises(ValueError):
            tm.build_features(self.rows("With"))

    def test_dataset_types_are_all_known(self):
        data = tm.load_dataset()
        self.assertLessEqual(set(data["statement_type"]), set(tm.STATEMENT_TYPES))


if __name__ == "__main__":
    unittest.main()
