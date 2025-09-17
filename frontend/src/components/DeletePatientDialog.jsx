import React, { useState } from 'react';
import { Button } from './ui/button';
import { AlertTriangle, User, FileText, Trash2 } from 'lucide-react';

const DeletePatientDialog = ({ 
  patient, 
  isOpen, 
  onClose, 
  onConfirm, 
  activeProcedures = 0 
}) => {
  const [deleteType, setDeleteType] = useState('soft'); // 'soft' or 'hard'
  const [isConfirming, setIsConfirming] = useState(false);

  if (!isOpen || !patient) return null;

  const handleConfirm = async () => {
    setIsConfirming(true);
    try {
      await onConfirm(deleteType === 'hard');
    } finally {
      setIsConfirming(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
        <div className="flex items-center space-x-3 mb-4">
          <div className="flex-shrink-0">
            <AlertTriangle className="h-6 w-6 text-orange-500" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Delete Patient
            </h3>
            <p className="text-sm text-gray-600">
              This action affects {patient.firstName} {patient.lastName}
            </p>
          </div>
        </div>

        {/* Patient Info */}
        <div className="bg-gray-50 rounded-lg p-3 mb-4">
          <div className="flex items-center space-x-2">
            <User className="h-4 w-4 text-gray-600" />
            <span className="font-medium">{patient.firstName} {patient.lastName}</span>
          </div>
          <p className="text-sm text-gray-600 ml-6">{patient.email}</p>
          {activeProcedures > 0 && (
            <div className="flex items-center space-x-2 mt-2">
              <FileText className="h-4 w-4 text-blue-600" />
              <span className="text-sm text-blue-600">
                {activeProcedures} active procedure assignment{activeProcedures !== 1 ? 's' : ''}
              </span>
            </div>
          )}
        </div>

        {/* Delete Options */}
        <div className="space-y-3 mb-6">
          <label className="flex items-start space-x-3 cursor-pointer">
            <input
              type="radio"
              name="deleteType"
              value="soft"
              checked={deleteType === 'soft'}
              onChange={(e) => setDeleteType(e.target.value)}
              className="mt-1"
            />
            <div>
              <div className="font-medium text-green-700">Mark as Inactive (Recommended)</div>
              <div className="text-sm text-gray-600">
                Patient will be hidden from lists but all procedure assignments will be preserved. 
                This option can be reversed.
              </div>
            </div>
          </label>

          <label className="flex items-start space-x-3 cursor-pointer">
            <input
              type="radio"
              name="deleteType"
              value="hard"
              checked={deleteType === 'hard'}
              onChange={(e) => setDeleteType(e.target.value)}
              className="mt-1"
            />
            <div>
              <div className="font-medium text-red-700">Permanently Delete</div>
              <div className="text-sm text-gray-600">
                ⚠️ <strong>WARNING:</strong> This will permanently remove the patient and all their 
                procedure assignments from the system. This action cannot be undone.
              </div>
            </div>
          </label>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isConfirming}
          >
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={isConfirming}
            className={`${
              deleteType === 'hard' 
                ? 'bg-red-600 hover:bg-red-700' 
                : 'bg-orange-600 hover:bg-orange-700'
            } text-white`}
          >
            {isConfirming ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                {deleteType === 'hard' ? 'Deleting...' : 'Deactivating...'}
              </>
            ) : (
              <>
                <Trash2 className="h-4 w-4 mr-2" />
                {deleteType === 'hard' ? 'Delete Permanently' : 'Mark Inactive'}
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default DeletePatientDialog;