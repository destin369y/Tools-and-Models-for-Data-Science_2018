//COMP543, A3
//Destin Liu

import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.util.ToolRunner;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.conf.Configured;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.PriorityQueue;
import java.util.regex.Pattern;
import java.util.regex.Matcher;

public class task2 extends Configured implements Tool {

  static int printUsage() {
    System.out.println("task2 [-m <maps>] [-r <reduces>] <input> <output>");
    ToolRunner.printGenericCommandUsage(System.out);
    return -1;
  }

  public static class task2Mapper1 extends Mapper<Object, Text, Text, DoubleWritable> {

    private final static DoubleWritable cost = new DoubleWritable(0);
    private Text practice = new Text();

    public void map(Object key, Text value, Context context) throws IOException, InterruptedException {
    	
    	try{
        	String line = value.toString();
    		String[] arr = line.split(",");
    		String pra = arr[2];
    		double nic = Double.parseDouble(arr[6]);
    		
    		practice.set(pra);
    		cost.set(nic);
        	context.write(practice, cost);
    	} catch(Exception e) {
    		//throw exception
    	}
    	
    }
  }

  public static class task2Reducer1 extends Reducer<Text, DoubleWritable, Text, DoubleWritable> {
    
	private DoubleWritable result = new DoubleWritable();

    public void reduce(Text key, Iterable<DoubleWritable> values, Context context) throws IOException, InterruptedException {
    	
    	double sumCost = 0.0;
    	for (DoubleWritable val : values) {
    		sumCost += val.get();
    	}
		  
    	result.set(sumCost);
    	context.write(key, result);
    }
  }

  public static class Pair {   
	    String practice;  
	    double cost;  
	    public Pair(String practice, double cost) {  
	        this.practice = practice;  
	        this.cost = cost;  
	    }  
	      
	    public String toString() {  
	        return practice + " " + cost;  
	    }  
	}  
  
  public static class task2Mapper2 extends Mapper<Object, Text, IntWritable, Text> {

	private IntWritable key = new IntWritable(1);
	private Text temp = new Text();
	private PriorityQueue<Pair> pq = new PriorityQueue<Pair>(
		new Comparator<Pair>() {
            public int compare(Pair p1, Pair p2) {  
            	return (int) (p2.cost - p1.cost); 
            }  
		}
    );
    
    public void map(Object key, Text value, Context context) throws IOException, InterruptedException {  	
    	try {
    		String[] line = value.toString().split("\t");
    		String practice = line[0];
    		double cost = Double.parseDouble(line[1]);
    		Pair p = new Pair(practice, cost);
        	pq.offer(p);
    	} catch(Exception e) {
    		//throw exception
    	}    	
    }
    
    public void cleanup(Context context) throws IOException, InterruptedException {    	
    	for (int i = 0; i < 5; i++) {
    		if (pq.isEmpty()) {
    			return;
    		}
        	Pair curPair = pq.poll();
    		temp.set(curPair.toString());
        	context.write(key, temp);
    	}
    }
    
  }

  public static class task2Reducer2 extends Reducer<IntWritable, Text, Text, DoubleWritable> {
    
	private Text text = new Text();
	private DoubleWritable result = new DoubleWritable();
	private PriorityQueue<Pair> pq = new PriorityQueue<Pair>(
			new Comparator<Pair>() {
	            public int compare(Pair p1, Pair p2) {  
	            	return (int) (p2.cost - p1.cost); 
	            }  
			}
	    );    

    public void reduce(IntWritable key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
    	for (Text val : values) {
    		String[] line = val.toString().split("\\s+");
    		String practice = line[0];
    		double cost = Double.parseDouble(line[1]);
    		Pair p = new Pair(practice, cost);
        	pq.offer(p);
    	}
    	
    	for (int i = 0; i < 5; i++) {
    		if (pq.isEmpty()) {
    			return;
    		}
        	Pair curPair = pq.poll();
        	text.set(curPair.practice);
        	result.set(curPair.cost);
        	context.write(text, result);
    	} 
    }

  }

  
  public int run(String[] args) throws Exception {

    Configuration conf = new Configuration();
    
    //String inputPath = "/input/";
    String mr1OutputPath = "/task2Output/mr1/";
    String mr2OutputPath = "/task2Output/mr2/";

    Job job1 = Job.getInstance(conf, "task2job1");
    job1.setJarByClass(task2.class);
    job1.setMapperClass(task2Mapper1.class);
    //job1.setCombinerClass(task2Reducer1.class);
    job1.setReducerClass(task2Reducer1.class);
    job1.setOutputKeyClass(Text.class);
    job1.setOutputValueClass(DoubleWritable.class);
    FileOutputFormat.setOutputPath(job1, new Path(mr1OutputPath));
    
    Job job2 = Job.getInstance(conf, "task2job2");
    job2.setJarByClass(task2.class);
    job2.setMapperClass(task2Mapper2.class);
    //job2.setCombinerClass(task2Reducer2.class);
    job2.setReducerClass(task2Reducer2.class);
    job2.setMapOutputKeyClass(IntWritable.class); 
    job2.setMapOutputValueClass(Text.class);
    job2.setOutputKeyClass(Text.class);
    job2.setOutputValueClass(DoubleWritable.class);
    FileInputFormat.addInputPath(job2, new Path(mr1OutputPath));
    FileOutputFormat.setOutputPath(job2, new Path(mr2OutputPath));
    
    List<String> other_args = new ArrayList<String>();
    for(int i=0; i < args.length; ++i) {
      try {
        if ("-r".equals(args[i])) {
          job1.setNumReduceTasks(Integer.parseInt(args[++i]));
          job2.setNumReduceTasks(Integer.parseInt(args[i]));
        } else {
          other_args.add(args[i]);
        }
      } catch (NumberFormatException except) {
        System.out.println("ERROR: Integer expected instead of " + args[i]);
        return printUsage();
      } catch (ArrayIndexOutOfBoundsException except) {
        System.out.println("ERROR: Required parameter missing from " +
                           args[i-1]);
        return printUsage();
      }
    }
    // Make sure there are exactly 2 parameters left.
    if (other_args.size() != 2) {
      System.out.println("ERROR: Wrong number of parameters: " +
                         other_args.size() + " instead of 2.");
      return printUsage();
    }
    FileInputFormat.setInputPaths(job1, other_args.get(0));
    //FileOutputFormat.setOutputPath(job1, new Path(other_args.get(1)));
    if (job1.waitForCompletion(true)) {
    	return (job2.waitForCompletion(true) ? 0 : 1);
    } else {
    	return 1;
    }
    
  }
  
  public static void main(String[] args) throws Exception {
    int res = ToolRunner.run(new Configuration(), new task2(), args);
    System.exit(res);
  }

}
