# Template Separation Implementation Plan

## 🎯 Objective
Refactor the monolithic `LatexGenerator` into separate template-specific generators for better maintainability, scalability, and template isolation.

## 📋 Current Issues Fixed
- ✅ **Abstract formatting bug**: First character missing - improved regex pattern
- ❌ **Monolithic design**: All templates in one file causes maintenance issues
- ❌ **Template conflicts**: IEEE vs Springer vs ACM have vastly different structures  
- ❌ **Scalability issues**: Adding new templates becomes complex

## 🏗️ Architecture Plan

### 1. Create Directory Structure
```
backend/app/services/latex/
├── __init__.py
├── base_generator.py           # BaseLatexGenerator abstract class
├── ieee_generator.py           # IEEELatexGenerator
├── acm_generator.py            # ACMLatexGenerator
├── springer_generator.py      # SpringerLatexGenerator
├── generator_factory.py       # LatexGeneratorFactory
└── utils.py                    # Shared utilities
```

### 2. Template-Specific Differences Analysis

#### Abstract Formats:
- **IEEE**: `\begin{abstract}...\end{abstract}`
- **ACM**: `\begin{abstract}...\end{abstract}` (before maketitle)
- **Springer**: `\abstract{...}` (single command)

#### Keywords Formats:
- **IEEE**: `\begin{IEEEkeywords}...\end{IEEEkeywords}`
- **ACM**: `\keywords{...}`
- **Springer**: `\keywords{...}`

#### Author Formats:
- **IEEE**: `\IEEEauthorblockN{...}\IEEEauthorblockA{...}`
- **ACM**: `\author{...}\affiliation{...}`
- **Springer**: `\author[1]{\fnm{...} \sur{...}}\affil[1]{...}`

#### Document Classes:
- **IEEE**: `\documentclass[conference]{IEEEtran}`
- **ACM**: `\documentclass[acmtog]{acmart}`
- **Springer**: `\documentclass[pdflatex,sn-mathphys-num]{sn-jnl}`

### 3. Implementation Steps

#### Phase 1: Abstract Base Class
- Create `BaseLatexGenerator` abstract class
- Define common interface methods:
  - `generate()` - Main generation method
  - `_generate_preamble()` - Document class and packages
  - `_generate_title_section()` - Title and authors
  - `_generate_abstract()` - Abstract formatting
  - `_generate_keywords()` - Keywords formatting
  - `_generate_sections()` - Content sections
  - `_generate_bibliography()` - Bibliography
  - `_escape_latex()` - Utility method
  - `validate_latex()` - Validation method

#### Phase 2: Template-Specific Generators
- **IEEELatexGenerator**:
  - Document class: `IEEEtran`
  - Author format: `\IEEEauthorblockN` and `\IEEEauthorblockA`
  - Abstract: `\begin{abstract}...\end{abstract}`
  - Keywords: `\begin{IEEEkeywords}...\end{IEEEkeywords}`
  - Bibliography: `\begin{thebibliography}...\end{thebibliography}`

- **ACMLatexGenerator**:
  - Document class: `acmart`
  - Author format: `\author{...}\affiliation{...}`
  - Abstract: `\begin{abstract}...\end{abstract}` (before maketitle)
  - Keywords: `\keywords{...}`
  - Bibliography: `\bibliographystyle{ACM-Reference-Format}`

- **SpringerLatexGenerator**:
  - Document class: `sn-jnl`
  - Author format: `\author[1]{\fnm{...} \sur{...}}\affil[1]{...}`
  - Abstract: `\abstract{...}`
  - Keywords: `\keywords{...}`
  - Bibliography: `\begin{thebibliography}...\end{thebibliography}`

#### Phase 3: Factory Pattern
- Create `LatexGeneratorFactory`
- Map `LatexTemplate` enum to generator classes
- Handle instantiation and configuration

#### Phase 4: Integration
- Update main `latex_generator.py` to use factory
- Maintain backward compatibility
- Update service layer integration

### 4. Migration Strategy
1. Keep existing `LatexGenerator` as fallback
2. Implement new architecture alongside
3. Test each template separately
4. Switch to new architecture once verified
5. Remove old implementation

### 5. Testing Strategy
- Unit tests for each template generator
- Integration tests for factory pattern
- Template-specific LaTeX validation
- Comparison tests with current implementation

## 📝 Implementation TODO List

### High Priority
- [ ] Create `BaseLatexGenerator` abstract class
- [ ] Implement `IEEELatexGenerator` class
- [ ] Implement `ACMLatexGenerator` class
- [ ] Implement `SpringerLatexGenerator` class
- [ ] Create `LatexGeneratorFactory`
- [ ] Update main service to use factory pattern

### Medium Priority
- [ ] Create template architecture documentation
- [ ] Migrate existing template logic to new classes
- [ ] Add backward compatibility layer
- [ ] Update project documentation

### Low Priority
- [ ] Add comprehensive testing for each template
- [ ] Create template addition guide
- [ ] Performance optimization
- [ ] Add template validation

## 🎯 Benefits
1. **Isolation**: Template issues won't affect others
2. **Maintainability**: Each template has dedicated logic
3. **Scalability**: Easy to add new templates
4. **Testing**: Template-specific test coverage
5. **Debugging**: Easier to identify template-specific issues

## 📚 Reference Templates
Official templates location: `/Users/akshitharsola/Documents/Overleaf Automation/TEMPLATES/`
- `IEEE.tex` - IEEE Conference template
- `ACM.tex` - ACM Conference template
- `Springer.tex` - Springer Nature template

## 🔧 Current Status
- ✅ Abstract character issue fixed
- ❌ Template separation not implemented
- ❌ Factory pattern not implemented
- ❌ Individual generators not created

---

**Note**: This plan provides a roadmap for implementing proper template separation to improve maintainability and scalability of the LaTeX generation system.