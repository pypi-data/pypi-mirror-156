import numpy as np
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from azureml.automl.core.shared.exceptions import ClientException, ValidationException
from azureml.automl.dnn.nlp.classification.multiclass import runner
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import AutoNLPInternal
from azureml.automl.dnn.nlp.common.constants import ModelNames

from ...mocks import (
    aml_dataset_mock, aml_label_dataset_mock, get_multiclass_labeling_df, MockRun, multiclass_trainer_mock,
    open_classification_file
)


class TestMulticlassRunner:
    """Tests for Multiclass runner."""

    @pytest.mark.usefixtures('MulticlassDatasetTester')
    @pytest.mark.usefixtures('MulticlassValDatasetTester')
    @pytest.mark.parametrize('multiple_text_column', [True, False])
    @pytest.mark.parametrize('include_label_col', [True])
    @pytest.mark.parametrize('is_main_process', [True, False])
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoModelForSequenceClassification")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.get_model_from_language")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.is_main_process")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.initialize_log_server")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.prepare_run_properties")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_conda_yml")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner._get_input_example_dictionary")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner._get_output_example")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_deploy_script")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_script")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.prepare_post_run_properties")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_model_wrapper")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.Run.get_context")
    def test_runner_test(
            self,
            run_mock,
            save_model_mock,
            prepare_post_properties_mock,
            save_script_mock,
            save_deploy_script_mock,
            input_example_mock,
            output_example_mock,
            conda_yml_mock,
            prepare_properties_mock,
            initialize_log_server_mock,
            is_main_process_mock,
            tokenizer_mock,
            get_by_id_mock,
            language_mock,
            model_mock,
            trainer_mock,
            MulticlassDatasetTester,
            MulticlassValDatasetTester,
            is_main_process
    ):
        # run mock
        mock_run = MockRun()
        run_mock.return_value = mock_run

        # settings mock
        automl_settings = {
            "task_type": "text-classification",
            "primary_metric": "accuracy",
            "dataset_id": "mock_dataset_id",
            "validation_dataset_id": "mock_validation_dataset_id",
            "label_column_name": "labels_col"
        }
        mock_settings = MagicMock()
        mock_settings.dataset_id = "mock_dataset_id"
        mock_settings.validation_dataset_id = "mock_validation_dataset_id"
        mock_settings.label_column_name = "labels_col"
        mock_settings.primary_metric = "accuracy"
        mock_settings.save_mlflow = True
        initialize_log_server_mock.return_value = mock_settings
        is_main_process_mock.return_value = is_main_process

        # dataset get_by_id mock
        train_df = MulticlassDatasetTester.get_data().copy()
        val_df = MulticlassValDatasetTester.get_data().copy()
        concat_df = pd.concat([train_df, val_df], ignore_index=True)
        mock_aml_dataset = aml_dataset_mock(concat_df)
        get_by_id_mock.return_value = mock_aml_dataset

        # model mock
        model = MagicMock()
        model.from_pretrained.return_value = MagicMock()
        model_mock.return_value = model

        # tokenizer mock
        tokenizer = MagicMock()
        tokenizer.model_max_length = 128
        tokenizer_mock.from_pretrained.return_value = tokenizer

        # language mock
        language_mock.return_value = "bert-base-cased", "some_path"

        # save_mock
        save_deploy_script_mock.return_value = "mocked_deploy_file"
        input_example_mock.return_value = "mock_input_example"
        output_example_mock.return_value = "mock_output_example"

        # trainer mock
        mock_trainer = multiclass_trainer_mock(len(concat_df))
        trainer_mock.return_value = mock_trainer

        # Test runner
        runner.run(automl_settings)

        # Asserts
        mock_trainer.train.assert_called_once()
        mock_trainer.save_model.assert_called_once()
        mock_trainer.save_state.assert_called_once()
        mock_trainer.save_metrics.assert_called_once()

        if is_main_process is True:
            mock_trainer.validate.assert_called_once
        else:
            mock_trainer.validate.assert_not_called()

    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.initialize_log_server")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.Run")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.dataloader")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.TextClassificationTrainer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.prepare_post_run_properties")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_conda_yml")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_script")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_deploy_script")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner._get_input_example_dictionary")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner._get_output_example")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_model_wrapper")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner._get_language_code")
    def test_runner_language_continuity(self, language_mock, save_model_mock, input_example_mock,
                                        output_example_mock, deploy_mock, score_mock, conda_mock, post_run_mock,
                                        trainer_mock, dataload_mock, run_mock, parse_mock):
        run_mock.get_context.return_value = MockRun(
            label_column_name="label",
            featurization='{"_dataset_language":"mul"}'
        )
        run_mock.experiment.workspace = "some_workspace"
        parse_mock.return_value = MagicMock()
        parse_mock.return_value.validation_dataset_id = None
        parse_mock.return_value.primary_metric = "accuracy"
        parse_mock.return_value.save_mlflow = True

        language_mock.return_value = 'mul'

        dataload_mock.load_and_validate_multiclass_dataset.return_value =\
            MagicMock(), MagicMock(), np.array([0, 1, 2, 3, 4]),\
            np.array([0, 1, 2, 3]), np.array([1, 4, 3, 1, 2]), 128

        mock_trainer = multiclass_trainer_mock(5)
        trainer_mock.return_value = mock_trainer
        score_mock.return_value = MagicMock()
        deploy_mock.return_value = "mock_deploy_file"
        input_example_mock.return_value = "mock_input_example"
        output_example_mock.return_value = "mock_output_example"

        automl_settings = {
            "task_type": "text-classification",
            "primary_metric": "accuracy",
            "dataset_id": "mock_dataset_id",
            "validation_dataset_id": "mock_validation_dataset_id",
            "label_column_name": "label"
        }
        runner.run(automl_settings)
        assert dataload_mock.load_and_validate_multiclass_dataset.call_args[0][3].name_or_path ==\
            ModelNames.BERT_BASE_MULTILINGUAL_CASED
        assert trainer_mock.call_args[0][1] == "mul"

    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoModelForSequenceClassification")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.get_model_from_language")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.initialize_log_server")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.prepare_run_properties")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_conda_yml")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_script")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_deploy_script")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner._get_input_example_dictionary")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner._get_output_example")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.prepare_post_run_properties")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_model_wrapper")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.Run")
    def test_runner_test_labeling_run(
            self,
            run_mock,
            save_model_mock,
            prepare_post_properties_mock,
            input_example_mock,
            output_example_mock,
            save_deploy_mock,
            save_script_mock,
            conda_yml_mock,
            prepare_properties_mock,
            initialize_log_server_mock,
            tokenizer_mock,
            get_by_id_mock,
            language_mock,
            model_mock,
            trainer_mock
    ):
        # run mock
        mock_run = MockRun(run_source="Labeling", label_column_name="label", labeling_dataset_type="FileDataset")
        run_mock.get_context.return_value = mock_run

        # settings mock
        automl_settings = {
            "task_type": "text-classification",
            "primary_metric": "accuracy",
            "dataset_id": "mock_dataset_id",
            "validation_dataset_id": "mock_validation_dataset_id",
            "label_column_name": "label"
        }
        mock_settings = MagicMock()
        mock_settings.dataset_id = "mock_dataset_id"
        mock_settings.validation_dataset_id = "mock_validation_dataset_id"
        mock_settings.label_column_name = "label"
        mock_settings.primary_metric = "accuracy"
        mock_settings.save_mlflow = True
        initialize_log_server_mock.return_value = mock_settings

        # dataset get_by_id mock
        mock_aml_dataset = aml_label_dataset_mock('TextClassificationMultiClass', get_multiclass_labeling_df())
        get_by_id_mock.return_value = mock_aml_dataset

        # model mock
        model = MagicMock()
        model.from_pretrained.return_value = MagicMock()
        model_mock.return_value = model

        # tokenizer mock
        tokenizer = MagicMock()
        tokenizer.model_max_length = 128
        tokenizer_mock.from_pretrained.return_value = tokenizer

        # language mock
        language_mock.return_value = "bert-base-cased", "some_path"

        # save mock
        save_deploy_mock.return_value = "mock_deploy_file"
        input_example_mock.return_value = "mock_input_example"
        output_example_mock.return_value = "mock_output_example"

        # trainer mock
        mock_trainer = multiclass_trainer_mock(num_examples=60, num_cols=3)
        trainer_mock.return_value = mock_trainer

        # Test runner
        with patch("azureml.automl.dnn.nlp.classification.io.read._labeling_data_helper.open",
                   new=open_classification_file):
            runner.run(automl_settings)

        # Asserts
        mock_trainer.train.assert_called_once()
        mock_trainer.save_model.assert_called_once()
        mock_trainer.save_state.assert_called_once()
        mock_trainer.save_metrics.assert_called_once()

    @pytest.mark.usefixtures('MulticlassDatasetTester')
    @pytest.mark.parametrize('multiple_text_column', [True])
    @pytest.mark.parametrize('include_label_col', [True])
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.initialize_log_server")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.Run.get_context")
    def test_runner_test_without_validation_data(
            self,
            run_mock,
            initialize_log_server_mock,
            tokenizer_mock,
            get_by_id_mock,
            MulticlassDatasetTester
    ):
        # run mock
        mock_run = MockRun()
        run_mock.return_value = mock_run

        # settings mock
        automl_settings = {
            "task_type": "text-classification",
            "primary_metric": "accuracy",
            "dataset_id": "mock_dataset_id",
            "validation_dataset_id": None,
            "label_column_name": "labels_col"
        }
        mock_settings = MagicMock()
        mock_settings.dataset_id = "mock_dataset_id"
        mock_settings.validation_dataset_id = None
        mock_settings.label_column_name = "labels_col"
        mock_settings.primary_metric = "accuracy"
        mock_settings.save_mlfow = True
        initialize_log_server_mock.return_value = mock_settings

        # dataset get_by_id mock
        train_df = MulticlassDatasetTester.get_data().copy()
        mock_aml_dataset = aml_dataset_mock(train_df)
        get_by_id_mock.return_value = mock_aml_dataset

        # Runner will throw exception due to missing validation data
        with pytest.raises(ValidationException):
            runner.run(automl_settings)

    @pytest.mark.usefixtures('MulticlassDatasetTester')
    @pytest.mark.usefixtures('MulticlassValDatasetTester')
    @pytest.mark.parametrize('multiple_text_column', [False])
    @pytest.mark.parametrize('include_label_col', [True])
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoModelForSequenceClassification")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.get_model_from_language")
    @patch("azureml.data.abstract_dataset.AbstractDataset._load")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.is_main_process")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.initialize_log_server")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_conda_yml")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_script")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_deploy_script")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner._get_input_example_dictionary")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner._get_output_example")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.prepare_post_run_properties")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_model_wrapper")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.Run.get_context")
    def test_runner_test_mltable_data_json(
            self,
            run_mock,
            save_model_mock,
            prepare_post_properties_mock,
            input_example_mock,
            output_example_mock,
            save_deploy_mock,
            save_script_mock,
            conda_yml_mock,
            initialize_log_server_mock,
            is_main_process_mock,
            tokenizer_mock,
            dataset_load_mock,
            language_mock,
            model_mock,
            trainer_mock,
            MulticlassDatasetTester,
            MulticlassValDatasetTester
    ):
        # run mock
        mock_run = MockRun()
        run_mock.return_value = mock_run

        # settings mock
        automl_settings = {
            "task_type": "text-classification",
            "primary_metric": "accuracy",
            "label_column_name": "labels_col"
        }
        mock_settings = MagicMock()
        mock_settings.label_column_name = "labels_col"
        mock_settings.primary_metric = "accuracy"
        mock_settings.save_mlflow = True
        mltable_data_json = '{"TrainData": {"Uri": "azuremluri", "ResolvedUri": "resolved_uri"}, ' \
                            '"ValidData": {"Uri": "azuremluri2", "ResolvedUri": "resolved_uri2"}}'
        initialize_log_server_mock.return_value = mock_settings
        is_main_process_mock.return_value = True

        # dataset get_by_id mock
        train_df = MulticlassDatasetTester.get_data().copy()
        val_df = MulticlassValDatasetTester.get_data().copy()
        concat_df = pd.concat([train_df, val_df], ignore_index=True)
        mock_aml_dataset = aml_dataset_mock(concat_df)
        dataset_load_mock.return_value = mock_aml_dataset

        # model mock
        model = MagicMock()
        model.from_pretrained.return_value = MagicMock()
        model_mock.return_value = model

        # tokenizer mock
        tokenizer = MagicMock()
        tokenizer.model_max_length = 128
        tokenizer_mock.from_pretrained.return_value = tokenizer

        # language mock
        language_mock.return_value = "bert-base-cased", "some_path"

        # save mock
        save_deploy_mock.return_value = "mock_deploy_file"
        input_example_mock.return_value = "mock_input_example"
        output_example_mock.return_value = "mock_output_example"

        # trainer mock
        mock_trainer = multiclass_trainer_mock(len(concat_df))
        trainer_mock.return_value = mock_trainer

        # Test runner
        runner.run(automl_settings, mltable_data_json)

        # Asserts
        mock_trainer.train.assert_called_once()
        mock_trainer.save_model.assert_called_once()
        mock_trainer.save_state.assert_called_once()
        mock_trainer.save_metrics.assert_called_once()

    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.run_lifecycle_utilities.fail_run")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.Run.get_context")
    def test_runner_exception_scrubbing(self, run_mock, mock_fail_run):
        mock_run = MockRun()
        run_mock.return_value = mock_run

        automl_settings = {
            "task_type": "text-classification",
            "primary_metric": "accuracy",
            "label_column_name": "labels_col"
        }

        with pytest.raises(Exception):
            with patch("azureml.automl.dnn.nlp.classification.multiclass.runner."
                       "is_data_labeling_run_with_file_dataset", side_effect=Exception("It's a trap!")):
                runner.run(automl_settings)
        logged_exception = mock_fail_run.call_args[0][1]
        assert isinstance(logged_exception, ClientException)
        assert logged_exception.error_code == AutoNLPInternal.__name__
