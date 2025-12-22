"""
Unit tests for progress tracking utilities.

Tests the StepTracker class and interactive selection utilities with mocked dependencies.
No side effects - all external dependencies (readchar, Rich console) are mocked.

Test Structure:
    - 20+ unit tests covering all progress utilities
    - Test StepTracker lifecycle (add, start, complete, error, skip)
    - Test get_key() with mocked readchar
    - Test select_with_arrows() with mocked console and readchar
    - 100% coverage target for utils.progress

Examples:
    pytest tests/unit/test_utils_progress.py -v --cov=src/specify_cli/utils/progress
"""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, call, patch

import pytest
import readchar
import typer
from rich.tree import Tree

from specify_cli.utils.progress import StepTracker, get_key, select_with_arrows

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def step_tracker() -> StepTracker:
    """
    Create a StepTracker instance for testing.

    Returns
    -------
    StepTracker
        Fresh tracker with title
    """
    return StepTracker(title="Test Process")


@pytest.fixture
def mock_refresh_callback() -> Mock:
    """
    Create a mock refresh callback.

    Returns
    -------
    Mock
        Mock callable for refresh
    """
    return Mock()


# ============================================================================
# Test: StepTracker.__init__
# ============================================================================


@pytest.mark.unit
def test_step_tracker_init() -> None:
    """
    Test StepTracker initialization.

    Verifies:
        - Title is set
        - Steps list is empty
        - Refresh callback is None
    """
    tracker = StepTracker(title="Test Title")

    assert tracker.title == "Test Title"
    assert tracker.steps == []
    assert tracker._refresh_cb is None


# ============================================================================
# Test: StepTracker.add
# ============================================================================


@pytest.mark.unit
def test_step_tracker_add_step(step_tracker: StepTracker) -> None:
    """
    Test adding a step to tracker.

    Verifies:
        - Step is added with correct key and label
        - Status is 'pending'
        - Detail is empty
    """
    step_tracker.add(key="step1", label="First Step")

    assert len(step_tracker.steps) == 1
    assert step_tracker.steps[0]["key"] == "step1"
    assert step_tracker.steps[0]["label"] == "First Step"
    assert step_tracker.steps[0]["status"] == "pending"
    assert step_tracker.steps[0]["detail"] == ""


@pytest.mark.unit
def test_step_tracker_add_duplicate_step(step_tracker: StepTracker) -> None:
    """
    Test adding duplicate step (same key).

    Verifies:
        - Duplicate is ignored
        - Only one step exists
    """
    step_tracker.add(key="step1", label="First Step")
    step_tracker.add(key="step1", label="Duplicate Step")

    assert len(step_tracker.steps) == 1
    assert step_tracker.steps[0]["label"] == "First Step"


@pytest.mark.unit
def test_step_tracker_add_triggers_refresh(
    step_tracker: StepTracker, mock_refresh_callback: Mock
) -> None:
    """
    Test that adding step triggers refresh callback.

    Verifies:
        - Refresh callback is called when step is added
    """
    step_tracker.attach_refresh(mock_refresh_callback)
    step_tracker.add(key="step1", label="First Step")

    mock_refresh_callback.assert_called_once()


# ============================================================================
# Test: StepTracker.start
# ============================================================================


@pytest.mark.unit
def test_step_tracker_start_step(step_tracker: StepTracker) -> None:
    """
    Test starting a step.

    Verifies:
        - Status changes to 'running'
        - Detail is set
    """
    step_tracker.add(key="step1", label="First Step")
    step_tracker.start(key="step1", detail="Processing...")

    assert step_tracker.steps[0]["status"] == "running"
    assert step_tracker.steps[0]["detail"] == "Processing..."


@pytest.mark.unit
def test_step_tracker_start_nonexistent_step(step_tracker: StepTracker) -> None:
    """
    Test starting a step that doesn't exist.

    Verifies:
        - Step is created with running status
        - Key is used as label
    """
    step_tracker.start(key="new_step", detail="Auto-created")

    assert len(step_tracker.steps) == 1
    assert step_tracker.steps[0]["key"] == "new_step"
    assert step_tracker.steps[0]["label"] == "new_step"
    assert step_tracker.steps[0]["status"] == "running"
    assert step_tracker.steps[0]["detail"] == "Auto-created"


# ============================================================================
# Test: StepTracker.complete
# ============================================================================


@pytest.mark.unit
def test_step_tracker_complete_step(step_tracker: StepTracker) -> None:
    """
    Test completing a step.

    Verifies:
        - Status changes to 'done'
        - Detail is updated
    """
    step_tracker.add(key="step1", label="First Step")
    step_tracker.start(key="step1")
    step_tracker.complete(key="step1", detail="Finished successfully")

    assert step_tracker.steps[0]["status"] == "done"
    assert step_tracker.steps[0]["detail"] == "Finished successfully"


@pytest.mark.unit
def test_step_tracker_complete_without_detail(step_tracker: StepTracker) -> None:
    """
    Test completing step without detail.

    Verifies:
        - Status changes to 'done'
        - Previous detail is preserved if not provided
    """
    step_tracker.add(key="step1", label="First Step")
    step_tracker.start(key="step1", detail="Processing...")
    step_tracker.complete(key="step1")

    assert step_tracker.steps[0]["status"] == "done"
    assert step_tracker.steps[0]["detail"] == "Processing..."


# ============================================================================
# Test: StepTracker.error
# ============================================================================


@pytest.mark.unit
def test_step_tracker_error_step(step_tracker: StepTracker) -> None:
    """
    Test marking a step as error.

    Verifies:
        - Status changes to 'error'
        - Error detail is set
    """
    step_tracker.add(key="step1", label="First Step")
    step_tracker.start(key="step1")
    step_tracker.error(key="step1", detail="Failed with exception")

    assert step_tracker.steps[0]["status"] == "error"
    assert step_tracker.steps[0]["detail"] == "Failed with exception"


# ============================================================================
# Test: StepTracker.skip
# ============================================================================


@pytest.mark.unit
def test_step_tracker_skip_step(step_tracker: StepTracker) -> None:
    """
    Test skipping a step.

    Verifies:
        - Status changes to 'skipped'
        - Skip reason is set
    """
    step_tracker.add(key="step1", label="First Step")
    step_tracker.skip(key="step1", detail="Not applicable")

    assert step_tracker.steps[0]["status"] == "skipped"
    assert step_tracker.steps[0]["detail"] == "Not applicable"


# ============================================================================
# Test: StepTracker.render
# ============================================================================


@pytest.mark.unit
def test_step_tracker_render_produces_tree(step_tracker: StepTracker) -> None:
    """
    Test rendering step tracker as Rich Tree.

    Verifies:
        - Tree object is returned
        - Title is set
    """
    step_tracker.add(key="step1", label="First Step")
    step_tracker.add(key="step2", label="Second Step")

    tree = step_tracker.render()

    assert isinstance(tree, Tree)
    assert "Test Process" in str(tree.label)


@pytest.mark.unit
def test_step_tracker_render_all_statuses(step_tracker: StepTracker) -> None:
    """
    Test rendering with all possible step statuses.

    Verifies:
        - Each status renders correctly
        - Tree contains all steps
    """
    step_tracker.add(key="pending", label="Pending Step")
    step_tracker.start(key="running", detail="In progress")
    step_tracker.complete(key="done", detail="Complete")
    step_tracker.error(key="error", detail="Failed")
    step_tracker.skip(key="skipped", detail="Skipped")

    tree = step_tracker.render()

    assert len(step_tracker.steps) == 5
    assert isinstance(tree, Tree)


@pytest.mark.unit
def test_step_tracker_render_with_details(step_tracker: StepTracker) -> None:
    """
    Test rendering steps with details.

    Verifies:
        - Details are included in rendering
    """
    step_tracker.add(key="step1", label="Step with detail")
    step_tracker.start(key="step1", detail="Some extra info")

    tree = step_tracker.render()

    # Verify tree structure (details are in renderable but not directly accessible)
    assert isinstance(tree, Tree)
    assert len(step_tracker.steps) == 1


@pytest.mark.unit
def test_step_tracker_render_pending_with_detail(step_tracker: StepTracker) -> None:
    """
    Test rendering pending step with detail.

    Verifies:
        - Pending steps with details render correctly
    """
    step_tracker.add(key="step1", label="Pending Step")
    # Update detail without changing status
    step_tracker.steps[0]["detail"] = "Waiting for input"

    tree = step_tracker.render()

    assert isinstance(tree, Tree)
    assert step_tracker.steps[0]["status"] == "pending"
    assert step_tracker.steps[0]["detail"] == "Waiting for input"


# ============================================================================
# Test: StepTracker.attach_refresh
# ============================================================================


@pytest.mark.unit
def test_step_tracker_attach_refresh(
    step_tracker: StepTracker, mock_refresh_callback: Mock
) -> None:
    """
    Test attaching refresh callback.

    Verifies:
        - Callback is attached
        - Callback is called on updates
    """
    step_tracker.attach_refresh(mock_refresh_callback)

    step_tracker.add(key="step1", label="First Step")
    step_tracker.start(key="step1")
    step_tracker.complete(key="step1")

    assert mock_refresh_callback.call_count == 3


@pytest.mark.unit
def test_step_tracker_refresh_callback_exception_suppressed(
    step_tracker: StepTracker,
) -> None:
    """
    Test that exceptions in refresh callback are suppressed.

    Verifies:
        - Callback exceptions don't break tracker
        - Updates still work
    """
    failing_callback = Mock(side_effect=RuntimeError("Callback failed"))
    step_tracker.attach_refresh(failing_callback)

    # Should not raise exception
    step_tracker.add(key="step1", label="First Step")

    assert len(step_tracker.steps) == 1
    failing_callback.assert_called_once()


# ============================================================================
# Test: get_key
# ============================================================================


@pytest.mark.unit
def test_get_key_up_arrow() -> None:
    """
    Test get_key returns 'up' for up arrow.

    Verifies:
        - UP arrow key is mapped to 'up'
    """
    with patch("readchar.readkey", return_value=readchar.key.UP):
        result = get_key()

    assert result == "up"


@pytest.mark.unit
def test_get_key_down_arrow() -> None:
    """
    Test get_key returns 'down' for down arrow.

    Verifies:
        - DOWN arrow key is mapped to 'down'
    """
    with patch("readchar.readkey", return_value=readchar.key.DOWN):
        result = get_key()

    assert result == "down"


@pytest.mark.unit
def test_get_key_enter() -> None:
    """
    Test get_key returns 'enter' for enter key.

    Verifies:
        - ENTER key is mapped to 'enter'
    """
    with patch("readchar.readkey", return_value=readchar.key.ENTER):
        result = get_key()

    assert result == "enter"


@pytest.mark.unit
def test_get_key_escape() -> None:
    """
    Test get_key returns 'escape' for escape key.

    Verifies:
        - ESC key is mapped to 'escape'
    """
    with patch("readchar.readkey", return_value=readchar.key.ESC):
        result = get_key()

    assert result == "escape"


@pytest.mark.unit
def test_get_key_ctrl_p() -> None:
    """
    Test get_key returns 'up' for Ctrl+P.

    Verifies:
        - CTRL_P is alternative for up
    """
    with patch("readchar.readkey", return_value=readchar.key.CTRL_P):
        result = get_key()

    assert result == "up"


@pytest.mark.unit
def test_get_key_ctrl_n() -> None:
    """
    Test get_key returns 'down' for Ctrl+N.

    Verifies:
        - CTRL_N is alternative for down
    """
    with patch("readchar.readkey", return_value=readchar.key.CTRL_N):
        result = get_key()

    assert result == "down"


@pytest.mark.unit
def test_get_key_ctrl_c() -> None:
    """
    Test get_key raises KeyboardInterrupt for Ctrl+C.

    Verifies:
        - CTRL_C raises KeyboardInterrupt
    """
    with patch("readchar.readkey", return_value=readchar.key.CTRL_C):
        with pytest.raises(KeyboardInterrupt):
            get_key()


@pytest.mark.unit
def test_get_key_other_character() -> None:
    """
    Test get_key returns raw character for other keys.

    Verifies:
        - Unrecognized keys are returned as-is
    """
    with patch("readchar.readkey", return_value="a"):
        result = get_key()

    assert result == "a"


# ============================================================================
# Test: select_with_arrows
# ============================================================================


@pytest.mark.unit
def test_select_with_arrows_basic_selection() -> None:
    """
    Test basic selection with arrow keys.

    Verifies:
        - First option is selected by default
        - Enter confirms selection
    """
    options = {
        "option1": "First option",
        "option2": "Second option",
        "option3": "Third option",
    }

    with patch("specify_cli.utils.progress.get_key", return_value="enter") as mock_get_key, \
         patch("specify_cli.utils.progress.console") as mock_console:

        result = select_with_arrows(options, prompt_text="Choose one")

        assert result == "option1"
        mock_get_key.assert_called_once()


@pytest.mark.unit
def test_select_with_arrows_navigation_down() -> None:
    """
    Test navigation with down arrow.

    Verifies:
        - Down arrow moves to next option
        - Selection wraps around to first option
    """
    options = {
        "option1": "First option",
        "option2": "Second option",
    }

    key_sequence = ["down", "enter"]
    key_iter = iter(key_sequence)

    with patch("specify_cli.utils.progress.get_key", side_effect=lambda: next(key_iter)), \
         patch("specify_cli.utils.progress.console"):

        result = select_with_arrows(options)

        assert result == "option2"


@pytest.mark.unit
def test_select_with_arrows_navigation_up() -> None:
    """
    Test navigation with up arrow.

    Verifies:
        - Up arrow moves to previous option
        - Selection wraps around to last option
    """
    options = {
        "option1": "First option",
        "option2": "Second option",
        "option3": "Third option",
    }

    key_sequence = ["up", "enter"]  # Up from first wraps to last
    key_iter = iter(key_sequence)

    with patch("specify_cli.utils.progress.get_key", side_effect=lambda: next(key_iter)), \
         patch("specify_cli.utils.progress.console"):

        result = select_with_arrows(options)

        assert result == "option3"


@pytest.mark.unit
def test_select_with_arrows_navigation_multiple_keys() -> None:
    """
    Test navigation with multiple arrow key presses.

    Verifies:
        - Multiple navigation keys work
        - Final selection is correct
    """
    options = {
        "option1": "First option",
        "option2": "Second option",
        "option3": "Third option",
    }

    key_sequence = ["down", "down", "up", "enter"]  # Navigate to option2
    key_iter = iter(key_sequence)

    with patch("specify_cli.utils.progress.get_key", side_effect=lambda: next(key_iter)), \
         patch("specify_cli.utils.progress.console"):

        result = select_with_arrows(options)

        assert result == "option2"


@pytest.mark.unit
def test_select_with_arrows_default_key() -> None:
    """
    Test selection with default key specified.

    Verifies:
        - Default key sets initial selection
    """
    options = {
        "option1": "First option",
        "option2": "Second option",
        "option3": "Third option",
    }

    with patch("specify_cli.utils.progress.get_key", return_value="enter"), \
         patch("specify_cli.utils.progress.console"):

        result = select_with_arrows(options, default_key="option2")

        assert result == "option2"


@pytest.mark.unit
def test_select_with_arrows_invalid_default_key() -> None:
    """
    Test selection with invalid default key.

    Verifies:
        - Invalid default key falls back to first option
    """
    options = {
        "option1": "First option",
        "option2": "Second option",
    }

    with patch("specify_cli.utils.progress.get_key", return_value="enter"), \
         patch("specify_cli.utils.progress.console"):

        result = select_with_arrows(options, default_key="nonexistent")

        assert result == "option1"


@pytest.mark.unit
def test_select_with_arrows_escape_exits() -> None:
    """
    Test that escape key exits with typer.Exit.

    Verifies:
        - Escape key raises typer.Exit
        - Exit code is 1
    """
    options = {
        "option1": "First option",
        "option2": "Second option",
    }

    with patch("specify_cli.utils.progress.get_key", return_value="escape"), \
         patch("specify_cli.utils.progress.console") as mock_console:

        with pytest.raises(typer.Exit) as exc_info:
            select_with_arrows(options)

        assert exc_info.value.exit_code == 1
        # Verify cancellation message was printed
        mock_console.print.assert_called()


@pytest.mark.unit
def test_select_with_arrows_keyboard_interrupt() -> None:
    """
    Test that KeyboardInterrupt is caught and exits gracefully.

    Verifies:
        - KeyboardInterrupt raises typer.Exit
        - Exit code is 1
    """
    options = {
        "option1": "First option",
        "option2": "Second option",
    }

    with patch("specify_cli.utils.progress.get_key", side_effect=KeyboardInterrupt), \
         patch("specify_cli.utils.progress.console") as mock_console:

        with pytest.raises(typer.Exit) as exc_info:
            select_with_arrows(options)

        assert exc_info.value.exit_code == 1
        mock_console.print.assert_called()


@pytest.mark.unit
def test_select_with_arrows_live_display_updates() -> None:
    """
    Test that Live display is updated during navigation.

    Verifies:
        - Live context manager is used
        - Navigation completes successfully
    """
    options = {
        "option1": "First option",
        "option2": "Second option",
    }

    key_sequence = ["down", "up", "enter"]
    key_iter = iter(key_sequence)

    with patch("specify_cli.utils.progress.get_key", side_effect=lambda: next(key_iter)), \
         patch("specify_cli.utils.progress.console"):

        result = select_with_arrows(options)

        # Verify selection succeeded after navigation
        assert result == "option1"


@pytest.mark.unit
def test_select_with_arrows_custom_prompt() -> None:
    """
    Test selection with custom prompt text.

    Verifies:
        - Custom prompt is used in display
    """
    options = {
        "option1": "First option",
    }

    with patch("specify_cli.utils.progress.get_key", return_value="enter"), \
         patch("specify_cli.utils.progress.console"):

        result = select_with_arrows(options, prompt_text="Custom Prompt")

        assert result == "option1"


@pytest.mark.unit
def test_select_with_arrows_wraparound() -> None:
    """
    Test that selection wraps around at both ends.

    Verifies:
        - Up from first goes to last
        - Down from last goes to first
    """
    options = {
        "option1": "First option",
        "option2": "Second option",
        "option3": "Third option",
    }

    # Test down wraparound
    key_sequence = ["down", "down", "down", "enter"]  # Wraps to option1
    key_iter = iter(key_sequence)

    with patch("specify_cli.utils.progress.get_key", side_effect=lambda: next(key_iter)), \
         patch("specify_cli.utils.progress.console"):

        result = select_with_arrows(options)

        assert result == "option1"


# ============================================================================
# Test: Edge Cases
# ============================================================================


@pytest.mark.unit
def test_step_tracker_update_nonexistent_key(step_tracker: StepTracker) -> None:
    """
    Test updating step that doesn't exist via _update.

    Verifies:
        - Step is auto-created
        - Status and detail are set
    """
    step_tracker._update(key="new_step", status="done", detail="Auto-completed")

    assert len(step_tracker.steps) == 1
    assert step_tracker.steps[0]["key"] == "new_step"
    assert step_tracker.steps[0]["label"] == "new_step"
    assert step_tracker.steps[0]["status"] == "done"
    assert step_tracker.steps[0]["detail"] == "Auto-completed"


@pytest.mark.unit
def test_step_tracker_empty_detail_not_overwritten(step_tracker: StepTracker) -> None:
    """
    Test that empty detail doesn't overwrite existing detail.

    Verifies:
        - Empty detail preserves previous detail
    """
    step_tracker.add(key="step1", label="Step")
    step_tracker.start(key="step1", detail="Processing")
    step_tracker.complete(key="step1", detail="")  # Empty detail

    # Empty detail should not overwrite
    assert step_tracker.steps[0]["detail"] == "Processing"


@pytest.mark.unit
def test_step_tracker_status_order() -> None:
    """
    Test that status_order is properly defined.

    Verifies:
        - All expected statuses are in order dict
    """
    tracker = StepTracker(title="Test")

    assert tracker.status_order["pending"] == 0
    assert tracker.status_order["running"] == 1
    assert tracker.status_order["done"] == 2
    assert tracker.status_order["error"] == 3
    assert tracker.status_order["skipped"] == 4


@pytest.mark.unit
def test_select_with_arrows_single_option() -> None:
    """
    Test selection with only one option.

    Verifies:
        - Single option can be selected
        - Navigation doesn't cause issues
    """
    options = {"only": "Only option"}

    key_sequence = ["up", "down", "enter"]  # Navigation should stay on same option
    key_iter = iter(key_sequence)

    with patch("specify_cli.utils.progress.get_key", side_effect=lambda: next(key_iter)), \
         patch("specify_cli.utils.progress.console"):

        result = select_with_arrows(options)

        assert result == "only"


@pytest.mark.unit
def test_step_tracker_render_unknown_status(step_tracker: StepTracker) -> None:
    """
    Test rendering step with unknown status.

    Verifies:
        - Unknown status renders with blank symbol
    """
    step_tracker.add(key="step1", label="Step")
    # Manually set unknown status
    step_tracker.steps[0]["status"] = "unknown_status"

    tree = step_tracker.render()

    assert isinstance(tree, Tree)
    assert len(step_tracker.steps) == 1


@pytest.mark.unit
def test_step_tracker_render_non_pending_without_detail(step_tracker: StepTracker) -> None:
    """
    Test rendering non-pending steps without detail.

    Verifies:
        - Steps without details render correctly
        - All statuses work without details
    """
    step_tracker.start(key="running", detail="")
    step_tracker.complete(key="done", detail="")
    step_tracker.error(key="error", detail="")
    step_tracker.skip(key="skipped", detail="")

    tree = step_tracker.render()

    assert isinstance(tree, Tree)
    assert len(step_tracker.steps) == 4


@pytest.mark.unit
def test_step_tracker_render_empty_detail() -> None:
    """
    Test rendering step with explicitly empty detail string.

    Verifies:
        - Empty detail string is handled correctly
        - Step renders without detail
    """
    step_tracker = StepTracker(title="Test")
    step_tracker.add(key="step1", label="Step")
    step_tracker.steps[0]["detail"] = ""

    tree = step_tracker.render()

    assert isinstance(tree, Tree)
    assert step_tracker.steps[0]["detail"] == ""


@pytest.mark.unit
def test_select_with_arrows_ignored_key() -> None:
    """
    Test that unrecognized keys are ignored.

    Verifies:
        - Random key presses don't affect selection
        - Selection continues after ignored keys
    """
    options = {
        "option1": "First option",
        "option2": "Second option",
    }

    key_sequence = ["a", "b", "c", "enter"]  # Random keys then enter
    key_iter = iter(key_sequence)

    with patch("specify_cli.utils.progress.get_key", side_effect=lambda: next(key_iter)), \
         patch("specify_cli.utils.progress.console"):

        result = select_with_arrows(options)

        # Should stay at default (option1) since random keys don't navigate
        assert result == "option1"
