# shared-tools/aia-tools

Parse MIT App Inventor `.aia` submission files into structured Python data.

## Modules

| Module | Purpose |
|--------|---------|
| `aia_util.py` | Extract `.aia` archives → `blockly`/`components` JSON; entry point for testers |
| `blockly_util.py` | Query and match Blockly block trees (recursive subset matching) |
| `components_util.py` | Query App Inventor component trees (type checks, property checks) |
| `extract_aias.py` | CLI: copy + extract all `.aia` files for a marking session |

## Usage in tester modules

`test.py` (the marking runner) adds `shared-tools/aia-tools/` to `sys.path` automatically,
so tester modules can import directly:

```python
import aia_util
import blockly_util
import components_util
```

### Populate blockly/components columns

```python
import aia_util

def test(submissions):
    submissions = aia_util.read_all_aias(submissions)
    for idx, row in submissions.iterrows():
        blockly = json.loads(row["blockly"])
        components = json.loads(row["components"])
        # ... mark using blockly_util / components_util ...
    return submissions
```

### Key utilities

```python
# Check a component exists (any screen)
components_util.assert_has_type(components, ["Button", "Label"])

# Check a property value
components_util.assert_has_properties_value(components, "Label", "Text", "Hello")

# Find all blocks across screens
blocks = blockly_util.get_all_blocks(blockly)

# Check an event handler exists
blockly_util.assert_has_component_event(blockly, "Button", "Click")

# Check a set-property block inside an event
blockly_util.assert_has_set_block_inside_event(blockly, "Button", "Click", "Label", "Text")

# Recursive subset match on any block tree
blockly_util.match_blocks_subset(block, {"@type": "controls_if"})
```

## Standalone extraction

When testing locally without the full pipeline:

```bash
cd Subjects/S3-CMP/marking
python ../../../shared-tools/aia-tools/extract_aias.py --session 25_26_pai
```

This copies `.aia` files from `attachments/<assignment>/` to `aias/<assignment>/` and extracts them.
