import { useState } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getExpandedRowModel,
  getPaginationRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
  type ExpandedState,
} from '@tanstack/react-table';
import { ChevronDown, ChevronRight, ChevronUp, ChevronsUpDown } from 'lucide-react';
import type { StoreForecast } from '@/types';
import { ConfidenceBar } from './ConfidenceBar';
import { StatusBadge } from './StatusBadge';

interface ClusterTableProps {
  stores: StoreForecast[];
}

export function ClusterTable({ stores }: ClusterTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [expanded, setExpanded] = useState<ExpandedState>({});
  const [globalFilter, setGlobalFilter] = useState('');

  // Column definitions
  const columns: ColumnDef<StoreForecast>[] = [
    {
      id: 'expander',
      header: () => null,
      cell: ({ row }) => {
        return row.getCanExpand() ? (
          <button
            onClick={row.getToggleExpandedHandler()}
            className="text-text-secondary hover:text-text-primary transition-colors"
          >
            {row.getIsExpanded() ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </button>
        ) : null;
      },
      size: 40,
    },
    {
      accessorKey: 'store_name',
      header: 'Store',
      cell: ({ row }) => (
        <div>
          <div className="font-medium text-text-primary">{row.original.store_name}</div>
          <div className="text-xs text-text-secondary">{row.original.location}</div>
        </div>
      ),
    },
    {
      accessorKey: 'forecast_units',
      header: 'Forecast',
      cell: ({ row }) => (
        <span className="font-medium text-text-primary">
          {row.original.forecast_units?.toLocaleString() ?? 'N/A'} units
        </span>
      ),
    },
    {
      accessorKey: 'confidence',
      header: 'Confidence',
      cell: ({ row }) => <ConfidenceBar confidence={row.original.confidence} />,
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => <StatusBadge status={row.original.status} />,
    },
  ];

  const table = useReactTable({
    data: stores,
    columns,
    state: {
      sorting,
      expanded,
      globalFilter,
    },
    onSortingChange: setSorting,
    onExpandedChange: setExpanded,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getRowCanExpand: () => true,
    initialState: {
      pagination: {
        pageSize: 10,
      },
    },
  });

  const showPagination = stores.length > 10;

  return (
    <div className="space-y-4">
      {/* Search/Filter */}
      <div className="flex items-center gap-2">
        <input
          type="text"
          placeholder="Search stores..."
          value={globalFilter ?? ''}
          onChange={(e) => setGlobalFilter(e.target.value)}
          className="px-3 py-2 bg-card border border-border rounded-lg text-sm text-text-primary placeholder:text-text-secondary focus:outline-none focus:ring-2 focus:ring-accent"
        />
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
              <>
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
                {row.getIsExpanded() && (
                  <tr key={`${row.id}-expanded`}>
                    <td colSpan={columns.length} className="px-4 py-3 bg-card">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-text-secondary">Size: </span>
                          <span className="text-text-primary font-medium">
                            {row.original.size_sqft?.toLocaleString() ?? 'N/A'} sq ft
                          </span>
                        </div>
                        <div>
                          <span className="text-text-secondary">Size Tier: </span>
                          <span className="text-text-primary font-medium">
                            {row.original.size_tier ?? 'N/A'}
                          </span>
                        </div>
                        <div>
                          <span className="text-text-secondary">Income Level: </span>
                          <span className="text-text-primary font-medium">
                            {row.original.income_level
                              ? `$${(row.original.income_level / 1000).toFixed(0)}K`
                              : 'N/A'}
                          </span>
                        </div>
                        <div>
                          <span className="text-text-secondary">Foot Traffic: </span>
                          <span className="text-text-primary font-medium">
                            {row.original.foot_traffic?.toLocaleString() ?? 'N/A'}/day
                          </span>
                        </div>
                        <div>
                          <span className="text-text-secondary">Location Type: </span>
                          <span className="text-text-primary font-medium">
                            {row.original.mall_location !== undefined
                              ? (row.original.mall_location ? 'Mall' : 'Standalone')
                              : 'N/A'}
                          </span>
                        </div>
                        <div>
                          <span className="text-text-secondary">Store ID: </span>
                          <span className="text-text-primary font-medium">
                            {row.original.store_id ?? 'N/A'}
                          </span>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </>
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
              stores.length
            )}{' '}
            of {stores.length} stores
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
