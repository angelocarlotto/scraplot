"""
Data Analysis Script for Auction Data
Query and analyze scraped auction data
"""

import pandas as pd
import json
from typing import Optional
import os


class AuctionDataAnalyzer:
    """Analyzer for scraped auction data"""
    
    def __init__(self, data_path: str = 'data/auction_data.csv'):
        """
        Initialize analyzer with data
        
        Args:
            data_path: Path to the CSV or JSON data file
        """
        self.data_path = data_path
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load data from file"""
        if not os.path.exists(self.data_path):
            print(f"Data file not found: {self.data_path}")
            print("Please run scraper.py first to collect data.")
            return
        
        if self.data_path.endswith('.csv'):
            self.df = pd.read_csv(self.data_path)
        elif self.data_path.endswith('.json'):
            self.df = pd.read_json(self.data_path)
        else:
            raise ValueError("Unsupported file format. Use .csv or .json")
        
        print(f"Loaded {len(self.df)} auction items")
    
    def get_summary(self):
        """Get summary statistics of the data"""
        if self.df is None or self.df.empty:
            print("No data available")
            return
        
        print("\n" + "=" * 60)
        print("AUCTION DATA SUMMARY")
        print("=" * 60)
        print(f"Total Lots: {len(self.df)}")
        print(f"Columns: {', '.join(self.df.columns.tolist())}")
        print(f"\nLots per page:")
        print(self.df['page'].value_counts().sort_index())
        print("\nData Info:")
        print(self.df.info())
    
    def search_by_keyword(self, keyword: str, column: str = 'title'):
        """
        Search for items containing keyword
        
        Args:
            keyword: Search term
            column: Column to search in (default: 'title')
        """
        if self.df is None:
            return None
        
        mask = self.df[column].astype(str).str.contains(keyword, case=False, na=False)
        results = self.df[mask]
        
        print(f"\nFound {len(results)} items matching '{keyword}' in {column}:")
        return results
    
    def filter_by_page(self, page_num: int):
        """Get all lots from a specific page"""
        if self.df is None:
            return None
        
        results = self.df[self.df['page'] == page_num]
        print(f"\nPage {page_num} contains {len(results)} items:")
        return results
    
    def get_price_range(self, min_price: Optional[float] = None, max_price: Optional[float] = None):
        """
        Filter items by price range
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
        """
        if self.df is None:
            return None
        
        # This assumes current_bid column has numeric values
        # You may need to clean the data first
        try:
            df_copy = self.df.copy()
            df_copy['price_numeric'] = pd.to_numeric(
                df_copy['current_bid'].str.replace('$', '').str.replace(',', ''),
                errors='coerce'
            )
            
            if min_price is not None:
                df_copy = df_copy[df_copy['price_numeric'] >= min_price]
            if max_price is not None:
                df_copy = df_copy[df_copy['price_numeric'] <= max_price]
            
            print(f"\nFound {len(df_copy)} items in price range:")
            return df_copy
        except Exception as e:
            print(f"Error filtering by price: {e}")
            return None
    
    def show_sample(self, n: int = 5):
        """Show sample of the data"""
        if self.df is None:
            return
        
        print(f"\nShowing {min(n, len(self.df))} sample items:")
        print(self.df.head(n).to_string())
    
    def export_filtered(self, filtered_df: pd.DataFrame, filename: str):
        """Export filtered results to a new file"""
        if filtered_df is None or filtered_df.empty:
            print("No data to export")
            return
        
        output_path = f"data/{filename}"
        
        if filename.endswith('.csv'):
            filtered_df.to_csv(output_path, index=False)
        elif filename.endswith('.json'):
            filtered_df.to_json(output_path, orient='records', indent=2)
        elif filename.endswith('.xlsx'):
            filtered_df.to_excel(output_path, index=False)
        else:
            print("Unsupported format. Use .csv, .json, or .xlsx")
            return
        
        print(f"Exported {len(filtered_df)} items to {output_path}")


def interactive_mode():
    """Interactive query mode"""
    analyzer = AuctionDataAnalyzer()
    
    if analyzer.df is None:
        return
    
    print("\n" + "=" * 60)
    print("INTERACTIVE AUCTION DATA ANALYZER")
    print("=" * 60)
    print("\nAvailable commands:")
    print("  1. summary - Show data summary")
    print("  2. sample - Show sample data")
    print("  3. search - Search by keyword")
    print("  4. page - Filter by page number")
    print("  5. quit - Exit")
    print()
    
    while True:
        try:
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'quit':
                break
            elif command == 'summary':
                analyzer.get_summary()
            elif command == 'sample':
                n = input("How many items? (default 5): ").strip()
                n = int(n) if n else 5
                analyzer.show_sample(n)
            elif command == 'search':
                keyword = input("Enter keyword: ").strip()
                column = input("Search in column (default 'title'): ").strip() or 'title'
                results = analyzer.search_by_keyword(keyword, column)
                if results is not None and not results.empty:
                    print(results[['lot_number', 'title', 'current_bid']].to_string())
            elif command == 'page':
                page = int(input("Enter page number (1-8): ").strip())
                results = analyzer.filter_by_page(page)
                if results is not None and not results.empty:
                    print(results[['lot_number', 'title', 'current_bid']].to_string())
            else:
                print("Unknown command. Try: summary, sample, search, page, or quit")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main function"""
    print("Auction Data Analyzer")
    
    # Check if data exists
    if not os.path.exists('data/auction_data.csv'):
        print("\nNo data found. Please run scraper.py first to collect data.")
        return
    
    # Run interactive mode
    interactive_mode()


if __name__ == "__main__":
    main()
