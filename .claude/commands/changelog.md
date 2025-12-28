# Add Changelog Entry

Add a semantic changelog entry following Keep a Changelog format.

## Usage
```
/changelog [TYPE] [DESCRIPTION]
```

## Arguments
- `$1` - Change type: added, changed, deprecated, removed, fixed, security
- `$2` - Description of the change

## Instructions

Add a changelog entry for: `$1` - `$2`

Following the constitutional equation, edit the RDF source:

1. **Edit** `memory/changelog.ttl`:
   ```turtle
   :entry-YYYY-MM-DD-N
       a :ChangelogEntry ;
       :changeType "$1" ;
       :description "$2" ;
       :date "YYYY-MM-DD" ;
       :version "Unreleased" .
   ```

2. **Run** `ggen sync` to regenerate CHANGELOG.md

3. **Verify** the generated CHANGELOG.md

Categories (Keep a Changelog):
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Features to be removed
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes

Remember: Edit the TTL source, not CHANGELOG.md directly!
