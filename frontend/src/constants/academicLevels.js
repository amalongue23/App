export const ACADEMIC_LEVEL_OPTIONS = [
  { value: 'LICENCIATURA_1', label: '1º ano de Licenciatura' },
  { value: 'LICENCIATURA_2', label: '2º ano de Licenciatura' },
  { value: 'LICENCIATURA_3', label: '3º ano de Licenciatura' },
  { value: 'LICENCIATURA_4', label: '4º ano de Licenciatura' },
  { value: 'LICENCIATURA_5', label: '5º ano de Licenciatura' },
  { value: 'MESTRADO_1', label: '1º ano de Mestrado' },
  { value: 'MESTRADO_2', label: '2º ano de Mestrado' },
]

export function academicLevelLabel(value) {
  return ACADEMIC_LEVEL_OPTIONS.find((item) => item.value === value)?.label || 'Não definido'
}
