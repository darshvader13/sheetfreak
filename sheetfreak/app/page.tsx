"use client"

import React, { useState, useRef, KeyboardEvent } from 'react'
import { Input } from "@/components/ui/input"
import Header from "@/components/ui/Header"

interface Cells {
    [key: string]: string // cellID to cell value
}

interface CellRefs {
  [key: string]: HTMLTableCellElement | null
}

interface CellInputRefs {
  [key: string]: HTMLInputElement | null
}

const numRows = 24
const numCols = 6

const SheetfreakLandingPage = () => {
  const [cellValues, setCellValues] = useState(() => {
    const cells: Cells = {};
    for (let col = 65; col <= 65 + numCols; col++) {  // A to F
      for (let row = 1; row <= numRows; row++) {
        const cellId = `${String.fromCharCode(col)}${row}`
        if (cellId === 'C7') {
          cells[cellId] = 'Your AI Data Analyst Intern'
        } else {
          cells[cellId] = ''
        }
      }
    }
    return cells;
  })
  const [activeCell, setActiveCell] = useState<string>('A1')
  const cellRefs = useRef<CellRefs>({})
  const cellInputRefs = useRef<CellInputRefs>({})

  const handleCellChange = (value: string) => {
    setCellValues(prev => ({ ...prev, [activeCell]: value }));
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter'|| e.key === 'ArrowDown') {
      const nextRow = (parseInt(activeCell.slice(1)) + 1)
      if (nextRow <= numRows) {
        const nextCellIndex = activeCell[0] + nextRow
        setActiveCell(nextCellIndex);
        cellRefs.current[nextCellIndex]?.focus();
      }
    } else if (e.key === 'Tab' || e.key === 'ArrowRight') {
      e.preventDefault()
      let nextCol = activeCell[0].charCodeAt(0)+1
      if (nextCol <= 65 + numCols) {
        const nextCellCol = String.fromCharCode(nextCol)
        const nextCellIndex = nextCellCol + activeCell.slice(1)
        if (cellRefs.current[nextCellIndex]) {
          cellRefs.current[nextCellIndex]?.focus();
          setActiveCell(nextCellIndex);
        }
      } 
    } else if (e.key === 'ArrowUp') {
      const nextRow = (parseInt(activeCell.slice(1)) - 1)
      if (nextRow >= 1) {
        const nextCellIndex = activeCell[0] + nextRow
        setActiveCell(nextCellIndex);
        cellRefs.current[nextCellIndex]?.focus();
      }
    } else if (e.key === 'ArrowLeft') {
      let nextCol = activeCell[0].charCodeAt(0)-1
      if (nextCol >= 65) {
        const nextCellCol = String.fromCharCode(nextCol)
        const nextCellIndex = nextCellCol + activeCell.slice(1)
        if (cellRefs.current[nextCellIndex]) {
          cellRefs.current[nextCellIndex]?.focus();
          setActiveCell(nextCellIndex);
        }
      } 
    } else if (e.key.length === 1 || e.key === 'Backspace') {
      cellInputRefs.current[activeCell]?.focus()
    }
  }

  return (
    <div className="flex flex-col h-screen bg-background text-foreground">
      <Header />
      {/* Formula Bar */}
      <div className="flex items-center p-2 bg-background border-b pt-4">
        <div className="w-10 text-center font-bold">{activeCell}</div>
        <div className="flex-grow">
          <Input 
            value={cellValues[activeCell]}
            onChange={(e) => handleCellChange(e.target.value)}
            onKeyDown={(e) => handleKeyDown(e)}
          />
        </div>
      </div>

      {/* Spreadsheet Grid */}
      <div className="flex-grow overflow-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr>
              <th className="w-10"></th>
              {['A', 'B', 'C', 'D', 'E', 'F'].map(col => (
                <th key={col} className="w-32 bg-muted border text-center">{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: numRows }, (_, i) => i + 1).map(row => (
              <tr key={row}>
                <td className="bg-muted border text-center">{row}</td>
                {['A', 'B', 'C', 'D', 'E', 'F'].map(col => {
                  const cellId = `${col}${row}`;
                  return (
                    <td 
                      key={cellId}
                      ref={(el) => {
                        if (cellRefs.current) {
                          cellRefs.current[cellId] = el
                        }
                      }}
                      tabIndex={0}
                      className={`border ${activeCell === cellId ? 'bg-accent' : ''} text-sm`}
                      onClick={() => setActiveCell(cellId)}
                      onFocus={() => setActiveCell(cellId)}
                      onKeyDown={(e) => handleKeyDown(e)}
                    >
                      {activeCell === cellId ? (
                        <Input
                          ref={(el) => {
                            if (cellInputRefs.current) {
                              cellInputRefs.current[cellId] = el
                            }
                          }}
                          className="w-full h-full border-none focus:ring-0 rounded-none"
                          value={cellValues[cellId]}
                          onChange={(e) => handleCellChange(e.target.value)}
                        />
                      ) : (
                        cellValues[cellId]
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SheetfreakLandingPage;