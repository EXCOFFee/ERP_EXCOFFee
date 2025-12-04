import React from 'react';
import {
  DataGrid,
  GridColDef,
  GridRowsProp,
  GridToolbar,
  GridPaginationModel,
  GridSortModel,
  GridFilterModel,
  GridRowSelectionModel,
} from '@mui/x-data-grid';
import { Box, Paper } from '@mui/material';

interface DataTableProps {
  rows: GridRowsProp;
  columns: GridColDef[];
  loading?: boolean;
  pageSize?: number;
  rowCount?: number;
  paginationMode?: 'client' | 'server';
  sortingMode?: 'client' | 'server';
  filterMode?: 'client' | 'server';
  onPaginationChange?: (model: GridPaginationModel) => void;
  onSortChange?: (model: GridSortModel) => void;
  onFilterChange?: (model: GridFilterModel) => void;
  onRowSelectionChange?: (model: GridRowSelectionModel) => void;
  checkboxSelection?: boolean;
  disableRowSelectionOnClick?: boolean;
  autoHeight?: boolean;
  density?: 'compact' | 'standard' | 'comfortable';
  showToolbar?: boolean;
  getRowId?: (row: any) => string | number;
}

const DataTable: React.FC<DataTableProps> = ({
  rows,
  columns,
  loading = false,
  pageSize = 10,
  rowCount,
  paginationMode = 'client',
  sortingMode = 'client',
  filterMode = 'client',
  onPaginationChange,
  onSortChange,
  onFilterChange,
  onRowSelectionChange,
  checkboxSelection = false,
  disableRowSelectionOnClick = true,
  autoHeight = false,
  density = 'standard',
  showToolbar = true,
  getRowId,
}) => {
  const [paginationModel, setPaginationModel] = React.useState<GridPaginationModel>({
    page: 0,
    pageSize,
  });

  const handlePaginationChange = (model: GridPaginationModel) => {
    setPaginationModel(model);
    onPaginationChange?.(model);
  };

  return (
    <Paper sx={{ width: '100%' }}>
      <Box sx={{ height: autoHeight ? 'auto' : 600, width: '100%' }}>
        <DataGrid
          rows={rows}
          columns={columns}
          loading={loading}
          paginationModel={paginationModel}
          onPaginationModelChange={handlePaginationChange}
          pageSizeOptions={[5, 10, 25, 50, 100]}
          rowCount={rowCount}
          paginationMode={paginationMode}
          sortingMode={sortingMode}
          filterMode={filterMode}
          onSortModelChange={onSortChange}
          onFilterModelChange={onFilterChange}
          onRowSelectionModelChange={onRowSelectionChange}
          checkboxSelection={checkboxSelection}
          disableRowSelectionOnClick={disableRowSelectionOnClick}
          autoHeight={autoHeight}
          density={density}
          slots={showToolbar ? { toolbar: GridToolbar } : undefined}
          slotProps={{
            toolbar: {
              showQuickFilter: true,
              quickFilterProps: { debounceMs: 500 },
            },
          }}
          getRowId={getRowId}
          sx={{
            border: 'none',
            '& .MuiDataGrid-cell:focus': {
              outline: 'none',
            },
            '& .MuiDataGrid-row:hover': {
              backgroundColor: 'action.hover',
            },
          }}
        />
      </Box>
    </Paper>
  );
};

export default DataTable;
