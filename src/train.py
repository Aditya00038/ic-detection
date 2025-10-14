"""
IC Detection Training Script using YOLOv8
Author: Your Name
Description: Train YOLOv8 model for IC detection with custom parameters
"""

import os
import yaml
import argparse
from pathlib import Path
from ultralytics import YOLO
from datetime import datetime
import torch
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ICDetectionTrainer:
    """YOLOv8 Trainer for IC Detection"""
    
    def __init__(self, config_path='train_config.yaml'):
        """
        Initialize trainer
        
        Args:
            config_path: Path to training configuration file
        """
        self.config_path = config_path
        self.config = self.load_config()
        self.model = None
        
    def load_config(self):
        """Load training configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"✓ Loaded config from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"✗ Error loading config: {e}")
            raise
    
    def setup_directories(self):
        """Create necessary directories"""
        dirs = [
            'data/train/images',
            'data/train/labels',
            'data/val/images',
            'data/val/labels',
            'data/test/images',
            'data/test/labels',
            'models',
            'runs'
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        logger.info("✓ Directories created/verified")
    
    def check_cuda(self):
        """Check CUDA availability"""
        if torch.cuda.is_available():
            device = torch.cuda.get_device_name(0)
            logger.info(f"✓ CUDA available: {device}")
            logger.info(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
            return True
        else:
            logger.warning("⚠ CUDA not available. Training will use CPU (slower)")
            return False
    
    def validate_dataset(self):
        """Validate dataset structure"""
        data_path = Path(self.config.get('path', './data'))
        train_path = data_path / self.config.get('train', 'train/images')
        val_path = data_path / self.config.get('val', 'val/images')
        
        if not train_path.exists():
            logger.error(f"✗ Training images not found at {train_path}")
            return False
        
        if not val_path.exists():
            logger.error(f"✗ Validation images not found at {val_path}")
            return False
        
        # Count images
        train_images = len(list(train_path.glob('*.jpg'))) + len(list(train_path.glob('*.png')))
        val_images = len(list(val_path.glob('*.jpg'))) + len(list(val_path.glob('*.png')))
        
        logger.info(f"✓ Dataset validated:")
        logger.info(f"  Training images: {train_images}")
        logger.info(f"  Validation images: {val_images}")
        
        if train_images == 0:
            logger.error("✗ No training images found!")
            return False
        
        return True
    
    def load_model(self, model_name=None):
        """
        Load YOLOv8 model
        
        Args:
            model_name: Model variant (yolov8n, yolov8s, yolov8m, yolov8l, yolov8x)
        """
        if model_name is None:
            model_name = self.config.get('model', 'yolov8s.pt')
        
        try:
            self.model = YOLO(model_name)
            logger.info(f"✓ Loaded model: {model_name}")
            
            # Model info
            if hasattr(self.model.model, 'yaml'):
                params = sum(p.numel() for p in self.model.model.parameters())
                logger.info(f"  Parameters: {params/1e6:.1f}M")
            
            return self.model
        except Exception as e:
            logger.error(f"✗ Error loading model: {e}")
            raise
    
    def train(self, **kwargs):
        """
        Train the model
        
        Args:
            **kwargs: Additional training parameters (override config)
        """
        if self.model is None:
            self.load_model()
        
        # Merge config with kwargs
        train_params = {
            'data': self.config_path,
            'epochs': self.config.get('epochs', 100),
            'batch': self.config.get('batch', 16),
            'imgsz': self.config.get('imgsz', 640),
            'patience': self.config.get('patience', 50),
            'save': self.config.get('save', True),
            'device': self.config.get('device', 0),
            'workers': self.config.get('workers', 8),
            'project': self.config.get('project', 'runs/detect'),
            'name': self.config.get('name', f'ic_detection_{datetime.now().strftime("%Y%m%d_%H%M%S")}'),
            'exist_ok': self.config.get('exist_ok', False),
            'pretrained': self.config.get('pretrained', True),
            'optimizer': self.config.get('optimizer', 'auto'),
            'verbose': self.config.get('verbose', True),
            'seed': self.config.get('seed', 0),
            'deterministic': self.config.get('deterministic', True),
            'amp': self.config.get('amp', True),
            'plots': self.config.get('plots', True),
        }
        
        # Override with kwargs
        train_params.update(kwargs)
        
        logger.info("🚀 Starting training...")
        logger.info(f"  Config: {train_params}")
        
        try:
            # Train model
            results = self.model.train(**train_params)
            
            logger.info("✓ Training completed!")
            logger.info(f"  Results saved to: {results.save_dir}")
            
            # Save best model
            best_model_path = Path(results.save_dir) / 'weights' / 'best.pt'
            if best_model_path.exists():
                import shutil
                shutil.copy(best_model_path, 'models/best.pt')
                logger.info(f"✓ Best model saved to: models/best.pt")
            
            return results
            
        except Exception as e:
            logger.error(f"✗ Training error: {e}")
            raise
    
    def validate(self, model_path='models/best.pt'):
        """
        Validate trained model
        
        Args:
            model_path: Path to model weights
        """
        try:
            model = YOLO(model_path)
            logger.info(f"Validating model: {model_path}")
            
            results = model.val(data=self.config_path)
            
            logger.info("✓ Validation completed!")
            logger.info(f"  mAP50: {results.box.map50:.4f}")
            logger.info(f"  mAP50-95: {results.box.map:.4f}")
            logger.info(f"  Precision: {results.box.mp:.4f}")
            logger.info(f"  Recall: {results.box.mr:.4f}")
            
            return results
            
        except Exception as e:
            logger.error(f"✗ Validation error: {e}")
            raise
    
    def export_model(self, model_path='models/best.pt', format='onnx'):
        """
        Export model to different formats
        
        Args:
            model_path: Path to model weights
            format: Export format (onnx, torchscript, tflite, etc.)
        """
        try:
            model = YOLO(model_path)
            logger.info(f"Exporting model to {format.upper()} format...")
            
            export_path = model.export(format=format)
            
            logger.info(f"✓ Model exported to: {export_path}")
            return export_path
            
        except Exception as e:
            logger.error(f"✗ Export error: {e}")
            raise


def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description='Train YOLOv8 for IC Detection')
    
    # Training arguments
    parser.add_argument('--config', type=str, default='train_config.yaml',
                      help='Path to training config file')
    parser.add_argument('--model', type=str, default='yolov8s.pt',
                      help='Model variant (yolov8n/s/m/l/x.pt)')
    parser.add_argument('--epochs', type=int, default=None,
                      help='Number of training epochs')
    parser.add_argument('--batch', type=int, default=None,
                      help='Batch size')
    parser.add_argument('--imgsz', type=int, default=None,
                      help='Input image size')
    parser.add_argument('--device', type=str, default=None,
                      help='Device (0, 1, 2, ... or cpu)')
    parser.add_argument('--workers', type=int, default=None,
                      help='Number of worker threads')
    parser.add_argument('--name', type=str, default=None,
                      help='Experiment name')
    
    # Actions
    parser.add_argument('--validate', action='store_true',
                      help='Validate model after training')
    parser.add_argument('--export', type=str, default=None,
                      help='Export format (onnx, torchscript, tflite)')
    parser.add_argument('--resume', type=str, default=None,
                      help='Resume training from checkpoint')
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = ICDetectionTrainer(config_path=args.config)
    
    # Setup
    trainer.setup_directories()
    trainer.check_cuda()
    
    # Validate dataset
    if not trainer.validate_dataset():
        logger.error("Dataset validation failed. Please check your dataset structure.")
        return
    
    # Load model
    trainer.load_model(args.model)
    
    # Prepare training kwargs
    train_kwargs = {}
    if args.epochs: train_kwargs['epochs'] = args.epochs
    if args.batch: train_kwargs['batch'] = args.batch
    if args.imgsz: train_kwargs['imgsz'] = args.imgsz
    if args.device: train_kwargs['device'] = args.device
    if args.workers: train_kwargs['workers'] = args.workers
    if args.name: train_kwargs['name'] = args.name
    if args.resume: train_kwargs['resume'] = args.resume
    
    # Train
    logger.info("=" * 60)
    logger.info("IC DETECTION TRAINING - YOLOv8")
    logger.info("=" * 60)
    
    results = trainer.train(**train_kwargs)
    
    # Validate if requested
    if args.validate:
        logger.info("\n" + "=" * 60)
        logger.info("VALIDATION")
        logger.info("=" * 60)
        trainer.validate()
    
    # Export if requested
    if args.export:
        logger.info("\n" + "=" * 60)
        logger.info("EXPORT")
        logger.info("=" * 60)
        trainer.export_model(format=args.export)
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ TRAINING PIPELINE COMPLETED!")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
