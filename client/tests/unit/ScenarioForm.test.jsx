import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ScenarioForm from '@components/ScenarioForm.jsx'

// Mock the ImageUpload component
vi.mock('@components/ImageUpload.jsx', () => ({
  default: ({ onImageSelect, selectedImage, disabled }) => (
    <div data-testid="mock-image-upload">
      <span>Mock ImageUpload</span>
      <span>Selected: {selectedImage ? 'Yes' : 'No'}</span>
      <span>Disabled: {disabled ? 'Yes' : 'No'}</span>
      <button
        onClick={() => onImageSelect('data:image/png;base64,mock-image-data', 'mock-file')}
        data-testid="mock-select-image"
      >
        Select Image
      </button>
    </div>
  )
}))

describe('ScenarioForm Component', () => {
  const mockOnSubmit = vi.fn()
  const defaultProps = {
    onSubmit: mockOnSubmit,
    isConnected: true,
    isAnalyzing: false
  }

  beforeEach(() => {
    mockOnSubmit.mockClear()
  })

  it('renders form with correct title and elements', () => {
    render(<ScenarioForm {...defaultProps} />)

    expect(screen.getByText('📸 Análisis de Imagen Agrícola')).toBeInTheDocument()
    expect(screen.getByText('Condiciones Ambientales Predefinidas:')).toBeInTheDocument()
    expect(screen.getByText('🌍 Condiciones Ambientales')).toBeInTheDocument()
    expect(screen.getByRole('textbox')).toBeInTheDocument()
    expect(screen.getByText('🚀 Analizar Imagen')).toBeInTheDocument()
  })

  it('renders predefined environment buttons', () => {
    render(<ScenarioForm {...defaultProps} />)

    expect(screen.getByText('🌱 Condiciones Ideales')).toBeInTheDocument()
    expect(screen.getByText('🐛 Alta Humedad')).toBeInTheDocument()
    expect(screen.getByText('💧 Condiciones Secas')).toBeInTheDocument()
    expect(screen.getByText('🧪 pH Elevado')).toBeInTheDocument()
  })

  it('loads predefined environment when button is clicked', async () => {
    const user = userEvent.setup()
    render(<ScenarioForm {...defaultProps} />)

    const idealConditionsButton = screen.getByText('🌱 Condiciones Ideales')
    await user.click(idealConditionsButton)

    const textarea = screen.getByRole('textbox')
    expect(textarea.value).toBe('Humedad del suelo 65%, Temperatura 23°C, pH 6.7, sin viento fuerte')
  })

  it('allows manual environment description input', async () => {
    const user = userEvent.setup()
    render(<ScenarioForm {...defaultProps} />)

    const textarea = screen.getByRole('textbox')
    await user.type(textarea, 'Custom environment description')

    expect(textarea.value).toBe('Custom environment description')
  })

  it('submits form with correct data when valid', async () => {
    const user = userEvent.setup()
    render(<ScenarioForm {...defaultProps} />)

    // Select image through mock component
    const selectImageButton = screen.getByTestId('mock-select-image')
    await user.click(selectImageButton)

    // Add environment description
    const textarea = screen.getByRole('textbox')
    await user.type(textarea, 'Test environment')

    // Submit form
    const submitButton = screen.getByText('🚀 Analizar Imagen')
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith('mock-image-data', 'Test environment')
    })
  })

  it('shows analyzing state correctly', () => {
    render(<ScenarioForm {...defaultProps} isAnalyzing={true} />)

    expect(screen.getByText('Analizando...')).toBeInTheDocument()
    expect(screen.queryByText('🚀 Analizar Imagen')).not.toBeInTheDocument()

    // Check that submit button has spinner
    const submitButton = screen.getByRole('button', { name: /analizando/i })
    expect(submitButton).toBeInTheDocument()
  })

  it('disables form elements when analyzing', () => {
    render(<ScenarioForm {...defaultProps} isAnalyzing={true} />)

    const textarea = screen.getByRole('textbox')
    expect(textarea).toBeDisabled()

    const predefinedButtons = screen.getAllByRole('button').filter(button =>
      button.textContent?.includes('🌱') ||
      button.textContent?.includes('🐛') ||
      button.textContent?.includes('💧') ||
      button.textContent?.includes('🧪')
    )

    predefinedButtons.forEach(button => {
      expect(button).toBeDisabled()
    })
  })

  it('disables submit when not connected', () => {
    render(<ScenarioForm {...defaultProps} isConnected={false} />)

    const submitButton = screen.getByRole('button', { name: /analizar imagen/i })
    expect(submitButton).toBeDisabled()
    expect(submitButton).toHaveClass('cursor-not-allowed')
  })

  it('disables submit when no image selected', () => {
    render(<ScenarioForm {...defaultProps} />)

    const submitButton = screen.getByRole('button', { name: /analizar imagen/i })
    expect(submitButton).toBeDisabled()
  })

  it('disables submit when no environment description', async () => {
    const user = userEvent.setup()
    render(<ScenarioForm {...defaultProps} />)

    // Select image
    const selectImageButton = screen.getByTestId('mock-select-image')
    await user.click(selectImageButton)

    // Don't add environment description
    const submitButton = screen.getByRole('button', { name: /analizar imagen/i })
    expect(submitButton).toBeDisabled()
  })

  it('shows correct connection status', () => {
    const { rerender } = render(<ScenarioForm {...defaultProps} isConnected={true} />)

    expect(screen.getByText('🟢 Conectado al servidor')).toBeInTheDocument()

    rerender(<ScenarioForm {...defaultProps} isConnected={false} />)
    expect(screen.getByText('🔴 Desconectado del servidor')).toBeInTheDocument()
  })

  it('prevents form submission when required fields are missing', async () => {
    const user = userEvent.setup()
    render(<ScenarioForm {...defaultProps} />)

    // Try to submit without selecting image or adding environment description
    const submitButton = screen.getByText('🚀 Analizar Imagen')
    await user.click(submitButton)

    // Form should not submit because required fields are missing
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('handles form submission correctly', async () => {
    const user = userEvent.setup()
    render(<ScenarioForm {...defaultProps} />)

    // Mock image selection
    const selectImageButton = screen.getByTestId('mock-select-image')
    await user.click(selectImageButton)

    // Add environment description
    const textarea = screen.getByRole('textbox')
    await user.type(textarea, 'Test environment description')

    // Submit form
    const submitButton = screen.getByText('🚀 Analizar Imagen')
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledTimes(1)
    })
  })

  it('processes image data correctly for submission', async () => {
    const user = userEvent.setup()
    render(<ScenarioForm {...defaultProps} />)

    const selectImageButton = screen.getByTestId('mock-select-image')
    await user.click(selectImageButton)

    const textarea = screen.getByRole('textbox')
    await user.type(textarea, 'Test environment')

    const submitButton = screen.getByText('🚀 Analizar Imagen')
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith('mock-image-data', 'Test environment')
    })
  })
})
