import { useState } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
} from '@tanstack/react-table';
import { ChevronDown, ChevronUp, ChevronsUpDown } from 'lucide-react';
import type { ReplenishmentItem } from '@/types/replenishment';
import { UrgencyBadge } from './UrgencyBadge';
import { ReplenishmentStatusBadge } from './ReplenishmentStatusBadge';
import { ActionButtons } from './ActionButtons';

interface ReplenishmentTableProps {
  items: ReplenishmentItem[];
  onApprove: (itemId: string) => void;
  onReject: (itemId: string) => void;
}

// Urgency sorting order
const urgencyOrder = { High: 1, Medium: 2, Low: 3 };

export function ReplenishmentTable({ items, onApprove, onReject }: ReplenishmentTableProps) {
  const [sorting, setSorting] = useState<SortingState>([
    { id: 'urgency', desc: false }, // Sort by urgency (High first) by default
  ]);
  const [globalFilter, setGlobalFilter] = useState('');

  // Column definitions
  const columns: ColumnDef<ReplenishmentItem>[] = [
    {
      accessorKey: 'store_name',
      header: 'Store',
      cell: ({ row }) => (
        <div>
          <div className="font-medium text-text-primary">{row.original.store_name}</div>
          <div className="text-xs text-text-secondary">{row.original.store_id}</div>
        </div>
      ),
    },
    {
      accessorKey: 'product_name',
      header: 'Product',
      cell: ({ row }) => (
        <div>
          <div className="font-medium text-text-primary">{row.original.product_name}</div>
          <div className="text-xs text-text-secondary">{row.original.sku}</div>
        </div>
      ),
    },
    {
      accessorKey: 'quantity',
      header: 'Quantity',
      cell: ({ row }) => (
        <div className="text-text-primary font-medium">
          {row.original.quantity} units
        </div>
      ),
    },
    {
      accessorKey: 'current_stock',
      header: 'Current Stock',
      cell: ({ row }) => (
        <div className="text-text-secondary text-sm">
          {row.original.current_stock} units
        </div>
      ),
    },
    {
      accessorKey: 'urgency',
      header: 'Urgency',
      cell: ({ row }) => <UrgencyBadge urgency={row.original.urgency} />,
      sortingFn: (rowA, rowB) => {
        const urgencyA = urgencyOrder[rowA.original.urgency];
        const urgencyB = urgencyOrder[rowB.original.urgency];
        return urgencyA - urgencyB;
      },
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => <ReplenishmentStatusBadge status={row.original.status} />,
    },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => (
        <ActionButtons
          itemId={row.original.id}
          status={row.original.status}
          onApprove={onApprove}
          onReject={onReject}
        />
      ),
    },
  ];

  const table = useReactTable({
    data: items,
    columns,
    state: {
      sorting,
      globalFilter,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
        pageSize: 10,
      },
    },
  });

  const showPagination = items.length > 10;

  return (
    <div className="space-y-4">
      {/* Search/Filter */}
      <div className="flex items-center gap-4">
        <input
          type="text"
          placeholder="Search by store, product, or SKU..."
          value={globalFilter ?? ''}
          onChange={(e) => setGlobalFilter(e.target.value)}
          className="flex-1 px-3 py-2 bg-card border border-border rounded-lg text-sm text-text-primary placeholder:text-text-secondary focus:outline-none focus:ring-2 focus:ring-accent"
        />
        <div className="text-sm text-text-secondary">
          {table.getFilteredRowModel().rows.length} items
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id} className="border-b border-border">
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider"
                  >
                    {header.isPlaceholder ? null : (
                      <div
                        className={
                          header.column.getCanSort()
                            ? 'flex items-center gap-2 cursor-pointer select-none hover:text-text-primary transition-colors'
                            : ''
                        }
                        onClick={header.column.getToggleSortingHandler()}
                      >
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                        {header.column.getCanSort() && (
                          <span className="text-text-secondary">
                            {header.column.getIsSorted() === 'asc' ? (
                              <ChevronUp className="h-4 w-4" />
                            ) : header.column.getIsSorted() === 'desc' ? (
                              <ChevronDown className="h-4 w-4" />
                            ) : (
                              <ChevronsUpDown className="h-4 w-4" />
                            )}
                          </span>
                        )}
                      </div>
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                className="border-b border-border hover:bg-card-hover transition-colors"
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-3 text-sm">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {showPagination && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-text-secondary">
            Showing {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1} to{' '}
            {Math.min(
              (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
              items.length
            )}{' '}
            of {items.length} items
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="px-3 py-1 text-sm bg-card border border-border rounded hover:bg-card-hover disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <button
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="px-3 py-1 text-sm bg-card border border-border rounded hover:bg-card-hover disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
