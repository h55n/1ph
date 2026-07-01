import { render, screen } from '@testing-library/react'
import { PrestigeBadge } from '../components/PrestigeBadge'

describe('PrestigeBadge', () => {
  it('renders T1 badge correctly', () => {
    render(<PrestigeBadge tier="T1" />)
    const badge = screen.getByText('T1')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('text-yellow-400')
  })

  it('renders T2 badge correctly', () => {
    render(<PrestigeBadge tier="T2" />)
    const badge = screen.getByText('T2')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('text-slate-300')
  })

  it('does not render T3 badge', () => {
    const { container } = render(<PrestigeBadge tier="T3" />)
    expect(container).toBeEmptyDOMElement()
  })
})
