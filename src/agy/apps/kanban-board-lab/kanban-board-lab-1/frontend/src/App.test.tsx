import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from './App'

describe('App Smoke Test', () => {
  it('renders application title heading', () => {
    render(<App />)
    const heading = screen.getByRole('heading', { level: 1, name: /kanban board lab/i })
    expect(heading).toBeInTheDocument()
  })
})
