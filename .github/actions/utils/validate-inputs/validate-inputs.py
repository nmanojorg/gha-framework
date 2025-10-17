import os
import sys
import yaml

def group(name):
    print(f"::group::{name}")

def endgroup():
    print("::endgroup::")

def load_yaml_env(var_name, default=None):
    raw = os.environ.get(var_name, "")
    if not raw and default is not None:
        return default
    try:
        return yaml.safe_load(raw)
    except Exception:
        return default if default is not None else []

def is_number_string(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def value_present(inputs, key):
    """Returns True if the key is present and value is non-empty after stripping."""
    value = inputs.get(key, None)
    return value is not None and str(value).strip() != ""

def filter_dict_keys(d, allowed_keys):
    """Returns a dict with only keys present in allowed_keys."""
    return {k: v for k, v in d.items() if k in allowed_keys}

def validate_keys(inputs, required, optional, errors):
    group("Key Correspondence Validation")
    input_keys = set(inputs.keys())
    expected_keys = set(required) | set(optional)
    missing = expected_keys - input_keys
    extra = input_keys - expected_keys
    if missing:
        errors.append(f"? Missing keys in actionInputs: {', '.join(sorted(missing))}")
        print(f"Missing keys: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"? Extra keys in actionInputs: {', '.join(sorted(extra))}")
        print(f"Extra keys: {', '.join(sorted(extra))}")
    if not missing and not extra:
        print("All keys correctly present.")
    endgroup()

def validate_type_mapping(inputs, type_validation, errors):
    group("Type Mapping Validation")
    input_keys = set(inputs.keys())
    type_keys = set()
    for type_name, keys in (type_validation or {}).items():
        if not isinstance(keys, list):
            errors.append(f"? Type validation keys for '{type_name}' should be a list.")
            print(f"Type '{type_name}' keys not a list.")
            continue
        type_keys.update(keys)
    filtered_type_keys = set(k for k in type_keys if k in inputs)
    missing = input_keys - filtered_type_keys
    extra = filtered_type_keys - input_keys
    if missing:
        errors.append(f"? Keys missing in typeValidations: {', '.join(sorted(missing))}")
        print(f"Missing in typeValidations: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"? Extra keys in typeValidations: {', '.join(sorted(extra))}")
        print(f"Extra in typeValidations: {', '.join(sorted(extra))}")
    if not missing and not extra:
        print("Type mappings correct.")
    endgroup()

def validate_required_fields(inputs, required, errors):
    group("Required Inputs Validation")
    for key in required:
        if not value_present(inputs, key):
            errors.append(f"? Missing or empty required input: '{key}'")
            print(f"Missing or empty required: {key}")
        else:
            print(f"OK: {key} = {inputs[key]}")
    endgroup()

def validate_types(inputs, type_validation, required, optional, errors):
    group("Type Validation")
    supported_types = ["string", "booleanString", "numberString"]
    for typ, keys in (type_validation or {}).items():
        for key in keys:
            if (key in required and key in inputs) or (key in optional and value_present(inputs, key)):
                value = str(inputs.get(key, "")).strip()
                if typ == "booleanString":
                    if value.lower() not in ["true", "false"]:
                        errors.append(f"? Invalid booleanString for '{key}': '{value}' (expected 'true' or 'false')")
                        print(f"Invalid booleanString: {key} ({value})")
                    else:
                        print(f"OK: {key} is booleanString: {value}")
                elif typ == "numberString":
                    if not is_number_string(value):
                        errors.append(f"? Invalid numberString for '{key}': '{value}' (expected numeric string)")
                        print(f"Invalid numberString: {key} ({value})")
                    else:
                        print(f"OK: {key} is numberString: {value}")
                elif typ == "string":
                    print(f"OK: {key} is string: {value}")
                else:
                    errors.append(
                        f"? Unknown type validation '{typ}' for key '{key}'. Supported types: {', '.join(supported_types)}"
                    )
                    print(
                        f"Unknown type: {typ} for {key}. Supported types: {', '.join(supported_types)}"
                    )
    endgroup()

def validate_ranges(inputs, range_validation, required, optional, errors):
    if not range_validation:
        return
    group("Range Validation")
    for key, allowed_values in (range_validation or {}).items():
        if (key in required and key in inputs) or (key in optional and value_present(inputs, key)):
            value = str(inputs.get(key, "")).strip()
            if value == "":
                if key in required:
                    errors.append(f"? Missing or empty required input for range validation: '{key}'")
                    print(f"Missing required for range: {key}")
                continue
            if value not in allowed_values:
                errors.append(f"? Invalid value for '{key}': '{value}'. Allowed: {allowed_values}")
                print(f"Invalid value for range: {key} ({value})")
            else:
                print(f"OK: {key} in allowed values: {value}")
    endgroup()

def validate_file_paths(inputs, file_keys, required, optional, errors):
    if not file_keys:
        return
    group("File Path Validation")
    for key in file_keys:
        if (key in required and key in inputs) or (key in optional and value_present(inputs, key)):
            value = str(inputs.get(key, "")).strip()
            if value == "":
                if key in required:
                    errors.append(f"? Missing or empty required file input: '{key}'")
                    print(f"Missing or empty required file: {key}")
                continue
            if not os.path.isfile(value):
                errors.append(f"? File input '{key}' not found at path: {value}")
                print(f"Missing file: {key} ({value})")
            else:
                print(f"OK: {key} file found at {value}")
    endgroup()

def validate_delimiters(inputs, delimiter_map, required, optional, errors):
    if not delimiter_map:
        return
    group("Delimiter Validation")
    for key, delimiter in (delimiter_map or {}).items():
        if (key in required and key in inputs) or (key in optional and value_present(inputs, key)):
            value = str(inputs.get(key, "")).strip()
            if value == "":
                if key in required:
                    errors.append(f"? Missing or empty required input for delimiter validation: '{key}'")
                    print(f"Missing or empty required for delimiter: {key}")
                continue
            if delimiter not in value and any(d in value for d in set([',', ';', '|', ':', ' ']) - {delimiter}):
                errors.append(f"? Value for '{key}' does not contain the specified delimiter '{delimiter}': '{value}'")
                print(f"Delimiter '{delimiter}' not found in {key}: {value}")
            else:
                print(f"OK: {key} uses delimiter '{delimiter}' in value: {value}")
    endgroup()

def process_dependency_validations(inputs, dependency_validations):
    if not dependency_validations:
        return set()
    group("Dependency Validation")
    ignored_keys = set()
    for controller_key, config in (dependency_validations or {}).items():
        expected_value = str(config.get("expectedValue", "")).strip()
        dependent_inputs = config.get("dependentInputs", [])
        actual_value = str(inputs.get(controller_key, "")).strip()
        if actual_value != expected_value:
            ignored_keys.update(dependent_inputs)
            print(f"Skipping validation for {dependent_inputs} as '{controller_key}' is '{actual_value}' (expected: '{expected_value}')")
        else:
            print(f"Dependency met for {controller_key}: {actual_value}")
    endgroup()
    return ignored_keys

if __name__ == "__main__":

    print("***** Start Input Validation (YAML ONLY) *****")
    group("YAML Input Loading")
    try:
        print(os.environ.get('INPUT_ACTIONINPUTS', ''))
        inputs = yaml.safe_load(os.environ.get('INPUT_ACTIONINPUTS', '')) or {}
        print("Loaded actionInputs:", inputs)
    except Exception as e:
        print(f"? Failed to parse YAML from INPUT_ACTIONINPUTS: {e}")
        endgroup()
        sys.exit(1)
    endgroup()

    required = load_yaml_env('INPUT_REQUIREDINPUTS', [])
    optional = load_yaml_env('INPUT_OPTIONALINPUTS', [])
    file_keys = load_yaml_env('INPUT_FILESPATHINPUTS', [])
    type_validation = load_yaml_env('INPUT_TYPEVALIDATIONS', {})
    range_validation = load_yaml_env('INPUT_RANGEVALIDATIONS', {})
    delimiter_validations = load_yaml_env('INPUT_DELIMITERVALIDATIONS', {})
    dependency_validations = load_yaml_env('INPUT_DEPENDENCYVALIDATIONS', {})

    errors = []

    validate_keys(inputs, required, optional, errors)
    validate_type_mapping(inputs, type_validation, errors)
    ignored_due_to_dependency = process_dependency_validations(inputs, dependency_validations)

    # Filter configs after dependency logic
    filtered_inputs = {k: v for k, v in inputs.items() if k not in ignored_due_to_dependency}
    filtered_required = [k for k in required if k in filtered_inputs]
    filtered_optional = [k for k in optional if k in filtered_inputs]
    filtered_file_keys = [k for k in file_keys if k in filtered_inputs]
    filtered_range_validation = filter_dict_keys(range_validation, filtered_inputs.keys())
    filtered_delimiter_validations = filter_dict_keys(delimiter_validations, filtered_inputs.keys())

    validate_required_fields(filtered_inputs, filtered_required, errors)
    validate_types(filtered_inputs, type_validation, filtered_required, filtered_optional, errors)
    validate_ranges(filtered_inputs, filtered_range_validation, filtered_required, filtered_optional, errors)
    validate_file_paths(filtered_inputs, filtered_file_keys, filtered_required, filtered_optional, errors)
    validate_delimiters(filtered_inputs, filtered_delimiter_validations, filtered_required, filtered_optional, errors)

    group("Validation Summary")
    if errors:
        print("\n?? Validation failed with the following issues:")
        for err in errors:
            print(f"  - {err}")
        print("\n? *** [END] Validation Ended with Errors ***")
        endgroup()
        sys.exit(1)
    else:
        print("\n? All validations passed successfully.")
        print("***** End Input Validation *****")
        endgroup()
        sys.exit(0)