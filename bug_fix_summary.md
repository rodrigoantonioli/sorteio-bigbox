# Bug Fix Summary: `editar_sorteio_colaborador` Function

## Issue Description
The `editar_sorteio_colaborador` function in `app/routes/admin.py` (lines 797-820) had critical server-side validation vulnerabilities:

1. **Missing Store Validation**: Server only verified collaborator existence but not if they belonged to the same store as the original sorteio
2. **Missing Eligibility Validation**: Server didn't verify if the collaborator was eligible (`apto=True`)
3. **UI Pre-selection Issue**: Form pre-selected current collaborator even if inactive, causing potential UI/validation problems

## Security Risk
These vulnerabilities allowed malicious users to:
- Assign collaborators from different stores through form manipulation
- Assign inactive/ineligible collaborators via race conditions or direct API calls
- Bypass client-side filtering constraints

## Fix Implementation

### 1. Added Server-Side Store Validation
```python
# Server-side validation: ensure collaborator belongs to same store
if novo_colaborador.loja_id != sorteio.colaborador.loja_id:
    flash('Erro: O colaborador selecionado não pertence à mesma loja do sorteio original.', 'danger')
    return render_template('admin/editar_sorteio_colaborador.html', ...)
```

### 2. Added Server-Side Eligibility Validation
```python
# Server-side validation: ensure collaborator is eligible
if not novo_colaborador.apto:
    flash('Erro: O colaborador selecionado não está apto para participar de sorteios.', 'danger')
    return render_template('admin/editar_sorteio_colaborador.html', ...)
```

### 3. Fixed Form Pre-selection Logic
```python
# Pré-seleciona o colaborador atual no formulário apenas se ele ainda estiver apto
# e na lista de colaboradores elegíveis da mesma loja
if sorteio.colaborador.apto and sorteio.colaborador_id in [c.id for c in colaboradores_loja]:
    form.colaborador_id.data = sorteio.colaborador_id
```

## Files Modified
- `app/routes/admin.py`: Lines 797-820 (function `editar_sorteio_colaborador`)

## Security Benefits
- ✅ Prevents cross-store collaborator assignment attacks
- ✅ Blocks assignment of inactive/ineligible collaborators
- ✅ Maintains data integrity regardless of client-side manipulation
- ✅ Provides clear error messages for validation failures
- ✅ Improved UI behavior with conditional pre-selection

## Testing Recommendations
1. Test form manipulation attempts with collaborators from different stores
2. Test assignment of inactive collaborators (`apto=False`)
3. Verify UI behavior when current collaborator becomes inactive
4. Test race condition scenarios where collaborator eligibility changes between form load and submission