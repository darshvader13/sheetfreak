"use client"

import React, { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Link from 'next/link'
import { buttonVariants } from "@/components/ui/button"

interface Cells {
    [key: string]: string
}

const numRows = 24
const numCols = 6

const SheetfreakLandingPage = () => {
  const [activeCell, setActiveCell] = useState<string>('A1');
//   const [editingCell, setEditingCell] = useState<string | null>(null);
  const [cellValues, setCellValues] = useState(() => {
    const cells: Cells = {};
    for (let col = 65; col <= 65 + numCols; col++) {  // A to F
      for (let row = 1; row <= numRows; row++) {
        const cellId = `${String.fromCharCode(col)}${row}`;
        cells[cellId] = cellId === 'A1' ? 'sheetfreak' : '';
      }
    }
    return cells;
  });
  const cellRefs = useRef<{ [key: string]: (HTMLTableCellElement | null) }>({});

//   const inputRef = useRef<HTMLInputElement>(null);

  // useEffect(() => {
  //   if (editingCell && inputRef.current) {
  //     inputRef.current.focus();
  //   }
  // }, [editingCell]);

  const handleCellClick = (cellId: string) => {
    setActiveCell(cellId);
    // if (editingCell === null) {
    //   // Start editing on the next keypress
    //   const handleKeyPress = (e: globalThis.KeyboardEvent) => {
    //     if (e.key.length === 1) {
    //       setEditingCell(cellId);
    //       setCellValues(prev => ({ ...prev, [cellId]: e.key }));
    //     }
    //     document.removeEventListener('keydown', handleKeyPress);
    //   };
    //   document.addEventListener('keydown', handleKeyPress);
    // }
  };

//   const handleCellDoubleClick = (cellId: string) => {
//     setEditingCell(cellId);
//   };

  const handleCellChange = (value: string) => {
    setCellValues(prev => ({ ...prev, [activeCell]: value }));
  };

//   const handleCellBlur = () => {
//     setEditingCell(null);
//   };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter') {
      // Move to the next row
      const nextRow = parseInt(activeCell.slice(1)) + 1;
      if (nextRow <= numRows) {
        setActiveCell(activeCell[0] + nextRow);
      }
    }
  };

  const handleKeyDownTD = (e: KeyboardEvent) => {
    console.log("handleKeyDownTD")
    if (e.key === 'Enter') {
      // Move to the next row
      const nextRow = parseInt(activeCell.slice(1)) + 1;
      if (nextRow <= numRows) {
        setActiveCell(activeCell[0] + nextRow);
      }
    }
    // else if (e.key.length === 1) {
    //   setCellValues(prev => ({ ...prev, [activeCell]: e.key }));
    // }
  }

  // useEffect(() => {
  //   const keyPressListener = (e: Event) => handleKeyDown(e as unknown as KeyboardEvent)
  //   document.addEventListener('keydown', keyPressListener)
  // }, [])

  return (
    <div className="flex flex-col h-screen bg-background text-foreground">
      {/* Top Navigation */}
      <div className="flex items-center p-4 h-20">
        <div className="flex-grow">
          <h1 className="text-2xl font-bold text-primary">sheetfreak</h1>
        </div>
        <div className="space-x-2">
          <Link href="/login" className={buttonVariants({ variant: "default" })}>Login</Link>
          <Link href="/getstarted" className={buttonVariants({ variant: "default" })}>Get Started</Link>
        </div>
      </div>

      {/* Spreadsheet Toolbar with Navigation Links */}
      <div className="flex items-center p-2">
        <Link href="/features" className={buttonVariants({ variant: "ghost" })}>Features</Link>
        <Link href="/pricing" className={buttonVariants({ variant: "ghost" })}>Pricing</Link>
        <Link href="/try" className={buttonVariants({ variant: "ghost" })}>Try</Link>
      </div>

      {/* Formula Bar */}
      <div className="flex items-center p-2 bg-background border-b">
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
                      ref={(el) => (cellRefs.current[cellId] = el)}
                      tabIndex={0}
                      // className={`border ${activeCell === cellId ? 'bg-accent' : ''}`}
                      // onClick={() => setActiveCell(cellId)}
                      // onFocus={() => setActiveCell(cellId)}
                      // onKeyDown={(e) => handleKeyDownTD(e)}
                      
                    //   onDoubleClick={() => handleCellDoubleClick(cellId)}
                    >
                      {/* {activeCell === cellId ? (
                        <Input
                          // ref={inputRef}
                          className="w-full h-full border-none focus:ring-0 rounded-none"
                          value={cellValues[cellId]}
                          onChange={(e) => handleCellChange(e.target.value)}
                          // onBlur={handleCellBlur}
                          onKeyDown={(e) => handleKeyDown(e)}
                        />
                      ) : (
                        cellValues[cellId]
                      )} */}
                      {cellValues[cellId]}
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