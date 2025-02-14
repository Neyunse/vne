import re

def increment_version(version_str, part="patch", pre_release=None, incr_suffix=False, only_pre_release=False):
    """
    Increments the version, supporting increments in the main part and/or in the pre-release suffix.

    Parameters:
      - version_str: Current version (e.g. "v1.0.0", "v1.0.0-alpha", "v1.0.0-alpha.1").
      - part: Part to increment: "major", "minor", or "patch". Used only if only_pre_release is False.
      - pre_release: Desired pre-release tag (e.g. "alpha", "beta"). If None, no suffix is added.
      - incr_suffix: If True and in only_pre_release mode, increments the numeric suffix.
      - only_pre_release: If True, the main part is not modified and only the pre-release suffix is updated (or incremented).

    Returns:
      The new version with the "v" prefix.
    """
    # Remove the 'v' prefix if it exists
    if version_str.startswith("v"):
        version_str = version_str[1:]
    
    # Separate the main version from the possible pre-release part
    main_version, sep, current_pre = version_str.partition("-")
    
    if only_pre_release:
        # The main part is not modified
        new_main = main_version
    else:
        # Increment the main part as indicated
        try:
            major, minor, patch = map(int, main_version.split('.'))
        except ValueError:
            raise ValueError("The version format must be 'major.minor.patch' (e.g. 1.0.0)")
    
        if part == "major":
            major += 1
            minor = 0
            patch = 0
        elif part == "minor":
            minor += 1
            patch = 0
        elif part == "patch":
            patch += 1
        else:
            raise ValueError("The part to increment must be 'major', 'minor', or 'patch'")
    
        new_main = f"{major}.{minor}.{patch}"
    
    new_pre = ""
    if pre_release:
        if only_pre_release:
            # In only pre_release mode, attempt to increment the numeric suffix if it already exists
            if current_pre and current_pre.startswith(pre_release):
                if incr_suffix:
                    # Check if there is a number after the suffix, for example, "alpha.1"
                    m = re.match(rf'({pre_release})(\.(\d+))?$', current_pre)
                    if m:
                        base = m.group(1)
                        num = m.group(3)
                        if num is None:
                            new_pre = f"{base}.1"
                        else:
                            new_pre = f"{base}.{int(num) + 1}"
                    else:
                        # If it doesn't match the pattern, assign the suffix with .1
                        new_pre = f"{pre_release}.1"
                else:
                    new_pre = pre_release
            else:
                # If there is no current suffix or it doesn't match, assign the given pre_release
                new_pre = pre_release
        else:
            # In normal mode, if pre_release is specified, simply attach it (without checking the previous one)
            new_pre = pre_release
    
    # Build the new version
    if new_pre:
        new_version = f"{new_main}-{new_pre}"
    else:
        new_version = new_main
    
    return f"v{new_version}"

def update_version_file(file_path, new_version):
    """
    Updates the file that contains the __version__ variable.
    
    It is expected that the file contains a line in the format:
      __version__ = "v1.0.0"
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    new_content = re.sub(
        r'(__version__\s*=\s*")[^"]*(")',
        rf'\1{new_version}\2',
        content
    )
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(new_content)

if __name__ == "__main__":
    version_file = "vne/_version.py"
    
    # Read the current version
    with open(version_file, "r", encoding="utf-8") as file:
        content = file.read()
    match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError("Version not found in the file.")
    current_version = match.group(1)
    
    """
    Configuration:
      - If you only want to update the main part, leave only_pre_release as False.
        Example: from v1.0.0 to v1.0.1 (or v2.0.0, etc.)
      
      - If you want to start or update a pre-release cycle without changing the main part,
        set only_pre_release = True.
        Additionally, if you want the suffix to increment (e.g. from "alpha.1" to "alpha.2"),
        set incr_suffix = True.
    
    Examples:
      1. Increment the main part (patch) and set a pre-release suffix:
           part = "patch"
           pre_release = "alpha"
           only_pre_release = False
           => If the version is v1.0.0, it will become v1.0.1-alpha
      
      2. Increment only the pre-release suffix:
           part = "patch"  (not used in this mode)
           pre_release = "alpha"
           only_pre_release = True
           incr_suffix = True
           => If the version is v1.0.0-alpha.1, it will become v1.0.0-alpha.2
    """
    
    # Example configuration:
    part = "patch"              # Or "minor", "major" as required (used only if only_pre_release is False)
    pre_release = "alpha"         # Change or set to None if no suffix is required
    only_pre_release = False      # Set to True to update only the suffix
    incr_suffix = False           # Useful only in only_pre_release mode to increment the numeric suffix
    
    # To test suffix increment without changing the main part, uncomment:
    # only_pre_release = True
    # incr_suffix = True
    
    new_version = increment_version(current_version, part, pre_release, incr_suffix, only_pre_release)
    update_version_file(version_file, new_version)
    
    print(f"Version updated from {current_version} to {new_version}")
