"""
Tests for the token_scheduler module.

This module contains tests for the token_scheduler.py module which provides
functionality to schedule token rewards for users.
"""

import os
import sys
import pytest
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
from descidb.token_scheduler import run_reward_users


class TestTokenScheduler:
    """Test suite for token_scheduler module."""

    def test_run_reward_users(self):
        """Test the token reward process scheduling."""
        with patch("descidb.token_scheduler.TokenRewarder") as mock_rewarder:
            with patch("descidb.token_scheduler.Path") as mock_path:
                with patch("descidb.token_scheduler.logger") as mock_logger:
                    # Configure path mock properly
                    mock_path_instance = MagicMock()
                    mock_path.return_value = mock_path_instance
                    mock_path_instance.parent.parent = "/mock/project/root"

                    # Configure TokenRewarder mock
                    mock_rewarder_instance = Mock()
                    mock_rewarder.return_value = mock_rewarder_instance

                    # Call the function
                    run_reward_users()

                    # Verify logger was called for start and completion
                    mock_logger.info.assert_any_call("Starting token reward process")
                    mock_logger.info.assert_any_call("Token reward process completed")

                    # Verify TokenRewarder was initialized with correct parameters
                    mock_rewarder.assert_called_once()
                    _, kwargs = mock_rewarder.call_args
                    assert kwargs["network"] == "test_base"
                    assert (
                        kwargs["contract_address"]
                        == "0x14436f6895B8EC34e0E4994Df29D1856b665B490"
                    )
                    assert "db_components" in kwargs
                    assert kwargs["host"] == "localhost"
                    assert kwargs["port"] == 5432

                    # Verify components structure
                    components = kwargs["db_components"]
                    assert "converter" in components
                    assert "chunker" in components
                    assert "embedder" in components

                    # Verify get_user_rewards was called for each component
                    assert mock_rewarder_instance.get_user_rewards.call_count > 0

    def test_run_reward_users_with_exception(self):
        """Test exception handling during the token reward process."""
        with patch("descidb.token_scheduler.TokenRewarder") as mock_rewarder:
            with patch("descidb.token_scheduler.Path"):
                with patch("descidb.token_scheduler.logger") as mock_logger:
                    # Configure TokenRewarder to raise an exception
                    mock_rewarder.side_effect = Exception("Test error")

                    # Call the function and expect an exception
                    with pytest.raises(Exception) as excinfo:
                        run_reward_users()

                    # Verify logger was called for start
                    mock_logger.info.assert_called_with("Starting token reward process")

                    # Verify the exception is passed through
                    assert "Test error" in str(excinfo.value)

    def test_run_reward_users_database_list(self):
        """Test that the database list is correctly constructed."""
        with patch("descidb.token_scheduler.TokenRewarder") as mock_rewarder:
            with patch("descidb.token_scheduler.Path"):
                with patch("descidb.token_scheduler.logger"):
                    # Capture the db_components argument
                    mock_rewarder_instance = Mock()
                    mock_rewarder.return_value = mock_rewarder_instance

                    # Call the function
                    run_reward_users()

                    # Verify call arguments and extract db_components
                    _, kwargs = mock_rewarder.call_args
                    components = kwargs["db_components"]

                    # Verify that components contain the expected values
                    assert "openai" in components["converter"]
                    assert "paragraph" in components["chunker"]
                    assert "sentence" in components["chunker"]
                    assert "openai" in components["embedder"]

                    # Verify uniqueness (list(set(x)) removes duplicates)
                    assert len(components["converter"]) == len(
                        set(components["converter"])
                    )
                    assert len(components["chunker"]) == len(set(components["chunker"]))
                    assert len(components["embedder"]) == len(
                        set(components["embedder"])
                    )

    def test_main_execution(self):
        """Test the script execution when run as __main__."""
        with patch("descidb.token_scheduler.run_reward_users") as mock_run:
            # Directly test the __name__ == "__main__" condition by mocking the entire module
            with patch.dict(
                "sys.modules", {"descidb.token_scheduler": Mock(__name__="__main__")}
            ):
                # Import the token_scheduler module to execute the __name__ == "__main__" block
                import importlib

                try:
                    # This might raise an ImportError since we're mocking the module
                    importlib.reload(importlib.import_module("descidb.token_scheduler"))
                except ImportError:
                    pass

                # Verify run_reward_users was called
                mock_run.assert_called_once()
